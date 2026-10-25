#!/usr/bin/env python3
"""Collect source-linked longevity-events candidates from approved public feeds."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCES = ROOT / "events" / "sources.json"
DEFAULT_SCHEMA = ROOT / "events" / "schemas" / "event-item.schema.json"
MAX_RESPONSE_BYTES = 5_000_000
RETENTION_DAYS = 90
USER_AGENT = (
    "VitaBiteLongevityEvents/1.0 "
    "(https://github.com/knightkalman/vitabite; metadata-only collector)"
)

LOCATION_PRECEDENCE: tuple[str, ...] = ("vienna", "europe", "us", "asia")
ALLOWED_LOCATIONS = {"vienna", "europe", "us", "asia", "other"}
ALLOWED_LOCATION_GROUPS = {"vienna", "europe", "us", "asia"}

US_VIENNA_DISAMBIGUATION: tuple[str, ...] = (
    "vienna, va",
    "vienna, virginia",
    "vienna virginia",
)

LOCATION_TERMS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "vienna",
        (
            "vienna",
            "wien",
            "hofburg",
            "austria center vienna",
            "medical university of vienna",
            "meduni wien",
        ),
    ),
    (
        "europe",
        (
            "europe",
            "european",
            "eugms",
            "ardd",
            "emas",
            "esmo",
            "easd",
            "eaps",
            "escp",
            "eacts",
            "austria",
            "austrian",
            "österreich",
            "österreichischen",
            "innsbruck",
            "graz",
            "salzburg",
            "germany",
            "german",
            "deutschland",
            "deutschen",
            "berlin",
            "munich",
            "münchen",
            "heidelberg",
            "tutzing",
            "frankfurt",
            "hamburg",
            "cologne",
            "switzerland",
            "swiss",
            "schweizerischen",
            "zurich",
            "zürich",
            "basel",
            "geneva",
            "st. gallen",
            "st gallen",
            "lausanne",
            "bern",
            "united kingdom",
            "british",
            "london",
            "oxford",
            "edinburgh",
            "manchester",
            "france",
            "french",
            "paris",
            "lyon",
            "nice",
            "netherlands",
            "dutch",
            "amsterdam",
            "rotterdam",
            "utrecht",
            "denmark",
            "danish",
            "copenhagen",
            "sweden",
            "swedish",
            "stockholm",
            "gothenburg",
            "norway",
            "norwegian",
            "oslo",
            "finland",
            "finnish",
            "helsinki",
            "iceland",
            "reykjavik",
            "belgium",
            "brussels",
            "spain",
            "spanish",
            "madrid",
            "barcelona",
            "valencia",
            "italy",
            "italian",
            "milan",
            "rome",
            "florence",
            "bologna",
            "portugal",
            "lisbon",
            "porto",
            "ireland",
            "dublin",
            "poland",
            "warsaw",
            "krakow",
            "czech",
            "prague",
            "hungary",
            "budapest",
            "greece",
            "athens",
        ),
    ),
    (
        "us",
        (
            "united states",
            "u.s.a.",
            "u.s.",
            "american",
            "national institute on aging",
            "midwest aging",
            "boston",
            "san francisco",
            "san diego",
            "los angeles",
            "new york",
            "bethesda",
            "washington, dc",
            "washington, d.c.",
            "chicago",
            "seattle",
            "austin",
            "miami",
            "philadelphia",
            "atlanta",
            "houston",
            "novato",
            "buck institute",
            "stanford",
            "harvard",
        ),
    ),
    (
        "asia",
        (
            "asia",
            "asian",
            "asia-pacific",
            "asia pacific",
            "apscvir",
            "timepie",
            "singapore",
            "japan",
            "japanese",
            "tokyo",
            "kyoto",
            "osaka",
            "yokohama",
            "korea",
            "korean",
            "seoul",
            "busan",
            "china",
            "chinese",
            "beijing",
            "shanghai",
            "shenzhen",
            "guangzhou",
            "hong kong",
            "taiwan",
            "taipei",
            "india",
            "indian",
            "mumbai",
            "bengaluru",
            "bangalore",
            "new delhi",
            "thailand",
            "bangkok",
            "malaysia",
            "kuala lumpur",
            "vietnam",
            "indonesia",
            "philippines",
            "manila",
            "israel",
            "tel aviv",
            "jerusalem",
            "dubai",
            "abu dhabi",
            "united arab emirates",
            "riyadh",
            "saudi arabia",
            "doha",
            "qatar",
        ),
    ),
)

TAG_TERMS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("conference", ("conference", "conferences")),
    ("symposium", ("symposium", "symposia")),
    ("congress", ("congress", "congresses", "jahrestagung")),
    ("workshop", ("workshop", "workshops")),
    ("summit", ("summit", "summits")),
    ("forum", ("forum", "forums", "colloquium")),
    ("meeting", ("meeting", "annual meeting", "scientific meeting")),
    ("consensus", ("consensus", "guideline", "guidelines")),
    ("geroscience", ("geroscience", "gerontology", "geriatric", "geriatrics", "aging", "ageing", "longevity")),
    ("nutrition", ("nutrition", "nutritional", "diet", "dietary", "metabolic", "diabetes", "obesity")),
    ("hybrid_or_online", ("virtual", "online", "webinar", "hybrid")),
)


class CollectionError(Exception):
    """A feed or response could not be safely processed."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def text_content(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join("".join(element.itertext()).split())


def fetch_bytes(url: str, *, timeout: int = 20, attempts: int = 3) -> bytes:
    """Fetch a bounded response with a descriptive UA and limited retries."""
    last_error: Exception | None = None
    for attempt in range(attempts):
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/rss+xml, application/atom+xml, application/json, application/xml, text/xml",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                final_host = urllib.parse.urlsplit(response.geturl()).hostname
                original_host = urllib.parse.urlsplit(url).hostname
                if final_host != original_host:
                    raise CollectionError("response redirected to a different host")
                payload = response.read(MAX_RESPONSE_BYTES + 1)
                if len(payload) > MAX_RESPONSE_BYTES:
                    raise CollectionError("response exceeded the 5 MB size limit")
                return payload
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(0.5 * (2**attempt))
        except CollectionError:
            raise
    raise CollectionError(f"request failed after {attempts} attempts: {last_error}")


def canonicalize_url(raw_url: str, allowed_domains: list[str]) -> str:
    parsed = urllib.parse.urlsplit(raw_url.strip())
    host = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme.lower() != "https" or not host or parsed.username or parsed.password:
        raise CollectionError("event URL must use HTTPS and have no embedded credentials")
    if not any(host == domain or host.endswith("." + domain) for domain in allowed_domains):
        raise CollectionError("event URL host is not in the source allowlist")

    filtered_query = [
        (key, value)
        for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
        and key.lower() not in {"fbclid", "gclid", "mc_cid", "mc_eid", "ref"}
    ]
    path = re.sub(r"/+$", "", parsed.path) or "/"
    return urllib.parse.urlunsplit(
        (
            "https",
            host,
            path,
            urllib.parse.urlencode(filtered_query, doseq=True),
            "",
        )
    )


def parse_date(raw_date: str) -> str | None:
    value = raw_date.strip()
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.date().isoformat()
    except ValueError:
        pass
    try:
        parsed = parsedate_to_datetime(value)
        return parsed.date().isoformat()
    except (TypeError, ValueError, OverflowError):
        return None


def parse_publication_date(raw_date: str) -> tuple[str | None, str, str | None]:
    value = raw_date.strip()
    if not value:
        return None, "unknown", None
    parsed = parse_date(value)
    if parsed:
        return parsed, "day", value[:80]
    if re.fullmatch(r"\d{4}", value):
        return None, "year", value
    partial_month = re.fullmatch(r"(\d{4})[\s/-]+([A-Za-z]+|\d{1,2})", value)
    if partial_month:
        month = partial_month.group(2)
        try:
            month_number = int(month) if month.isdigit() else datetime.strptime(
                month[:3], "%b"
            ).month
        except ValueError:
            return None, "unknown", value[:80]
        if 1 <= month_number <= 12:
            return None, "month", value[:80]
    return None, "unknown", value[:80]


def _keyword_matches(text: str, keyword: str) -> bool:
    pattern = r"(?<![a-z0-9äöüß])" + re.escape(keyword) + r"(?![a-z0-9äöüß])"
    return bool(re.search(pattern, text))


def normalize_location_groups(
    primary_location: str, groups: list[str] | set[str] | None = None
) -> tuple[str, list[str]]:
    group_set: set[str] = set()
    if groups:
        for group in groups:
            if group in ALLOWED_LOCATION_GROUPS:
                group_set.add(group)
    if primary_location in ALLOWED_LOCATION_GROUPS:
        group_set.add(primary_location)
    if "vienna" in group_set:
        group_set.add("europe")

    ordered_groups = [loc for loc in LOCATION_PRECEDENCE if loc in group_set]
    resolved_primary = ordered_groups[0] if ordered_groups else "other"
    return resolved_primary, ordered_groups


def classify_location(
    title: str,
    *,
    publisher: str | None = None,
    default_location: str | None = None,
) -> tuple[str, list[str], list[str]]:
    combined = f"{title} {publisher or ''}".casefold()
    is_us_vienna = any(term in combined for term in US_VIENNA_DISAMBIGUATION)
    scrubbed_for_vienna = combined
    if is_us_vienna:
        for term in US_VIENNA_DISAMBIGUATION:
            scrubbed_for_vienna = scrubbed_for_vienna.replace(term, " ")

    matched_groups: set[str] = set()
    if is_us_vienna:
        matched_groups.add("us")

    for region, keywords in LOCATION_TERMS:
        target_text = scrubbed_for_vienna if region == "vienna" else combined
        if any(_keyword_matches(target_text, keyword) for keyword in keywords):
            matched_groups.add(region)

    if not matched_groups and default_location in ALLOWED_LOCATION_GROUPS:
        matched_groups.add(default_location)

    primary_location, ordered_groups = normalize_location_groups(
        "other", matched_groups
    )

    tags: list[str] = ["needs_review"]
    tags.extend(ordered_groups)
    for tag, keywords in TAG_TERMS:
        if any(_keyword_matches(combined, keyword) for keyword in keywords):
            tags.append(tag)
    if not any(
        t in tags
        for t in ("conference", "symposium", "congress", "workshop", "summit", "forum", "meeting")
    ):
        tags.append("event")

    return primary_location, ordered_groups, sorted(set(tags))


def stable_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def build_candidate(
    *,
    source: dict[str, Any],
    upstream_id: str,
    title: str,
    article_url: str,
    publication_date: str | None,
    publication_date_precision: str | None = None,
    publication_date_raw: str | None = None,
    author: str | None,
    publisher: str | None = None,
    collected_at: str,
    run_id: str,
    access_basis: str,
) -> dict[str, Any]:
    clean_title = " ".join(title.split())
    if not clean_title or len(clean_title) > 500:
        raise CollectionError("event title is empty or exceeds 500 characters")
    canonical_url = canonicalize_url(article_url, source["allowed_domains"])
    resolved_publisher = (
        publisher.strip()[:250]
        if publisher and publisher.strip()
        else source["publisher"]
    )
    location, location_groups, tags = classify_location(
        clean_title,
        publisher=resolved_publisher,
        default_location=source.get("default_location"),
    )
    candidate = {
        "schema_version": 1,
        "item_id": stable_id(canonical_url),
        "source_id": source["source_id"],
        "source_record_id": str(upstream_id),
        "title": clean_title,
        "publisher": resolved_publisher,
        "author": " ".join(author.split())[:250] if author and author.strip() else None,
        "source_url": canonical_url,
        "publication_date": publication_date,
        "publication_date_precision": publication_date_precision
        or ("day" if publication_date else "unknown"),
        "publication_date_raw": publication_date_raw,
        "collected_at": collected_at,
        "content_access_basis": access_basis,
        "location": location,
        "location_groups": location_groups,
        "location_method": "rules_candidate",
        "tags": tags,
        "summary": None,
        "evidence_notes": None,
        "review_state": "candidate",
        "run_id": run_id,
        "last_updated": collected_at,
    }
    validate_candidate(candidate)
    return candidate


def validate_candidate(candidate: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "item_id",
        "source_id",
        "source_record_id",
        "title",
        "publisher",
        "author",
        "source_url",
        "publication_date",
        "publication_date_precision",
        "publication_date_raw",
        "collected_at",
        "content_access_basis",
        "location",
        "location_groups",
        "location_method",
        "tags",
        "summary",
        "evidence_notes",
        "review_state",
        "run_id",
        "last_updated",
    }
    if set(candidate) != required:
        raise CollectionError("candidate does not match the event-item schema fields")
    if candidate["schema_version"] != 1:
        raise CollectionError("unsupported candidate schema version")
    if candidate["location"] not in ALLOWED_LOCATIONS:
        raise CollectionError("candidate has an unknown location")
    if (
        not isinstance(candidate["location_groups"], list)
        or any(group not in ALLOWED_LOCATION_GROUPS for group in candidate["location_groups"])
        or len(candidate["location_groups"]) != len(set(candidate["location_groups"]))
    ):
        raise CollectionError("candidate location_groups must be unique valid region keys")
    if candidate["location"] == "vienna" and (
        "vienna" not in candidate["location_groups"]
        or "europe" not in candidate["location_groups"]
    ):
        raise CollectionError("vienna events must include both vienna and europe in location_groups")
    if (
        candidate["location"] in ALLOWED_LOCATION_GROUPS
        and candidate["location"] not in candidate["location_groups"]
    ):
        raise CollectionError("primary location must be present in location_groups")
    if candidate["location"] == "other" and candidate["location_groups"]:
        raise CollectionError("other location must have empty location_groups")
    if candidate["content_access_basis"] not in {
        "public_feed_metadata",
        "public_bibliographic_metadata",
    }:
        raise CollectionError("candidate has an unknown content-access basis")
    if candidate["review_state"] != "candidate" or candidate["summary"] is not None:
        raise CollectionError("collector output must remain an unsummarized candidate")
    if candidate["evidence_notes"] is not None:
        raise CollectionError("collector output must not invent evidence notes")
    if not isinstance(candidate["title"], str) or not candidate["title"].strip():
        raise CollectionError("candidate title must be non-empty text")
    if not isinstance(candidate["publisher"], str) or not candidate["publisher"].strip():
        raise CollectionError("candidate publisher must be non-empty text")
    if candidate["author"] is not None and not isinstance(candidate["author"], str):
        raise CollectionError("candidate author must be text or null")
    if not re.fullmatch(r"[a-f0-9]{64}", candidate["item_id"]):
        raise CollectionError("candidate item ID must be a SHA-256 hex digest")
    if not isinstance(candidate["source_url"], str):
        raise CollectionError("candidate source URL must be text")
    if stable_id(candidate["source_url"]) != candidate["item_id"]:
        raise CollectionError("candidate item ID does not match its canonical URL")
    if not candidate["source_url"].startswith("https://"):
        raise CollectionError("candidate source URL must use HTTPS")
    if candidate["publication_date"] is not None:
        try:
            date.fromisoformat(candidate["publication_date"])
        except (TypeError, ValueError) as error:
            raise CollectionError("candidate publication date must be an ISO date") from error
    if candidate["publication_date_precision"] not in {
        "day",
        "month",
        "year",
        "unknown",
    }:
        raise CollectionError("candidate publication-date precision is invalid")
    if candidate["publication_date_precision"] == "day" and not candidate[
        "publication_date"
    ]:
        raise CollectionError("day-precision dates must have a normalized publication date")
    if (
        candidate["publication_date_precision"] != "day"
        and candidate["publication_date"] is not None
    ):
        raise CollectionError("partial dates must not be represented as exact dates")
    if candidate["publication_date_raw"] is not None and not isinstance(
        candidate["publication_date_raw"], str
    ):
        raise CollectionError("raw publication date must be text or null")
    if (
        isinstance(candidate["publication_date_raw"], str)
        and len(candidate["publication_date_raw"]) > 80
    ):
        raise CollectionError("raw publication date exceeds 80 characters")
    for field in ("collected_at", "last_updated"):
        try:
            datetime.fromisoformat(candidate[field].replace("Z", "+00:00"))
        except (AttributeError, TypeError, ValueError) as error:
            raise CollectionError(f"candidate {field} must be an ISO timestamp") from error
    if not isinstance(candidate["tags"], list) or not all(
        isinstance(tag, str) and re.fullmatch(r"[a-z0-9][a-z0-9_-]*", tag)
        for tag in candidate["tags"]
    ):
        raise CollectionError("candidate tags must be normalized strings")
    if len(candidate["tags"]) != len(set(candidate["tags"])):
        raise CollectionError("candidate tags must be unique")


def parse_rss(source: dict[str, Any], payload: bytes, collected_at: str, run_id: str):
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as error:
        raise CollectionError(f"invalid RSS/XML: {error}") from error
    if local_name(root.tag) not in {"rdf", "rss", "feed"}:
        raise CollectionError("unsupported feed root element")

    entries = [element for element in root.iter() if local_name(element.tag) == "item"]
    if not entries and local_name(root.tag) == "feed":
        entries = [element for element in root if local_name(element.tag) == "entry"]

    candidates = []
    for entry in entries:
        fields = {local_name(child.tag): child for child in entry}
        title = text_content(fields.get("title"))
        link = text_content(fields.get("link"))
        if not link:
            link = entry.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")
        if not title or not link:
            continue
        filter_terms = source.get("filter_terms", [])
        if filter_terms and not any(
            term.casefold() in title.casefold() for term in filter_terms
        ):
            continue
        author_element = fields.get("creator")
        if author_element is None:
            author_element = fields.get("author")
        author = text_content(author_element) or None
        raw_date = (
            text_content(fields.get("date"))
            or text_content(fields.get("pubdate"))
            or text_content(fields.get("published"))
            or text_content(fields.get("publicationdate"))
        )
        pub_date, pub_precision, pub_raw = parse_publication_date(raw_date)
        try:
            candidate = build_candidate(
                source=source,
                upstream_id=link,
                title=title,
                article_url=link,
                publication_date=pub_date,
                publication_date_precision=pub_precision,
                publication_date_raw=pub_raw,
                author=author,
                collected_at=collected_at,
                run_id=run_id,
                access_basis="public_feed_metadata",
            )
        except CollectionError:
            continue
        candidates.append(candidate)
    return candidates


def fetch_pubmed(
    source: dict[str, Any], collected_at: str, run_id: str
) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode(
        {
            "db": "pubmed",
            "term": source["query"],
            "datetype": "pdat",
            "reldate": str(source["date_window_days"]),
            "retmax": str(source["max_results"]),
            "retmode": "json",
            "sort": "date",
        }
    )
    base = source["feed_url"].rstrip("/")
    search_url = f"{base}/esearch.fcgi?{query}"
    try:
        search = json.loads(fetch_bytes(search_url))
        identifiers = search["esearchresult"]["idlist"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise CollectionError(f"invalid PubMed ESearch response: {error}") from error
    if not identifiers:
        return []

    summary_query = urllib.parse.urlencode(
        {
            "db": "pubmed",
            "id": ",".join(identifiers),
            "retmode": "json",
            "version": "2.0",
        }
    )
    try:
        result = json.loads(fetch_bytes(f"{base}/esummary.fcgi?{summary_query}"))["result"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise CollectionError(f"invalid PubMed ESummary response: {error}") from error

    candidates = []
    for identifier in result.get("uids", identifiers):
        record = result.get(identifier)
        if not isinstance(record, dict):
            continue
        title = record.get("title", "")
        if not isinstance(title, str) or not title.strip():
            continue
        authors = record.get("authors", [])
        first_author = authors[0].get("name") if authors else None
        raw_date = record.get("pubdate", "") or record.get("epubdate", "")
        pub_date, pub_precision, pub_raw = parse_publication_date(raw_date)
        article_url = f"https://pubmed.ncbi.nlm.nih.gov/{identifier}/"
        try:
            candidate = build_candidate(
                source=source,
                upstream_id=identifier,
                title=title,
                article_url=article_url,
                publication_date=pub_date,
                publication_date_precision=pub_precision,
                publication_date_raw=pub_raw,
                author=first_author,
                publisher=record.get("fulljournalname"),
                collected_at=collected_at,
                run_id=run_id,
                access_basis="public_bibliographic_metadata",
            )
        except CollectionError:
            continue
        candidates.append(candidate)
    return candidates


def load_sources(path: Path) -> list[dict[str, Any]]:
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CollectionError(f"could not read source registry: {error}") from error
    if registry.get("registry_version") != 1 or not isinstance(
        registry.get("sources"), list
    ):
        raise CollectionError("source registry has an unsupported or invalid shape")
    seen_ids: set[str] = set()
    for source in registry["sources"]:
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or source_id in seen_ids:
            raise CollectionError("source IDs must be present and unique")
        seen_ids.add(source_id)
        if source.get("source_type") not in {"rss", "pubmed_eutils"}:
            raise CollectionError(f"{source_id} has an unsupported source type")
        for field in (
            "name",
            "publisher",
            "permitted_collection_method",
            "terms_notes",
            "trust_tier",
            "update_cadence",
        ):
            if not isinstance(source.get(field), str) or not source[field].strip():
                raise CollectionError(f"{source_id} has no valid {field}")
        if not isinstance(source.get("enabled"), bool):
            raise CollectionError(f"{source_id} enabled status must be boolean")
        if (
            "default_location" in source
            and source["default_location"] not in ALLOWED_LOCATIONS
        ):
            raise CollectionError(f"{source_id} has an invalid default_location")
        if not isinstance(source.get("topic_coverage"), list) or not source[
            "topic_coverage"
        ]:
            raise CollectionError(f"{source_id} has no topic coverage")
        try:
            date.fromisoformat(source["last_checked_date"])
        except (KeyError, TypeError, ValueError) as error:
            raise CollectionError(f"{source_id} has no valid last-checked date") from error
        if not isinstance(source.get("allowed_domains"), list) or not source[
            "allowed_domains"
        ]:
            raise CollectionError(f"{source_id} has no allowed event domains")
        parsed = urllib.parse.urlsplit(source.get("feed_url", ""))
        if parsed.scheme != "https" or not parsed.hostname:
            raise CollectionError(f"{source_id} feed URL must use HTTPS")
        if source["source_type"] == "rss" and source.get("format") not in {
            "rss1",
            "rss2",
        }:
            raise CollectionError(f"{source_id} has an unsupported RSS format")
        if source["source_type"] == "rss":
            feed_host = parsed.hostname.lower()
            if not any(
                feed_host == domain or feed_host.endswith("." + domain)
                for domain in source["allowed_domains"]
            ):
                raise CollectionError(f"{source_id} RSS host is outside its allowlist")
            filter_terms = source.get("filter_terms", [])
            if not isinstance(filter_terms, list) or any(
                not isinstance(term, str) or not term.strip() for term in filter_terms
            ):
                raise CollectionError(f"{source_id} has invalid title filter terms")
        if source["source_type"] == "pubmed_eutils":
            if source.get("format") != "json" or not isinstance(
                source.get("query"), str
            ):
                raise CollectionError(f"{source_id} has an invalid PubMed configuration")
            if not 1 <= source.get("date_window_days", 0) <= 730:
                raise CollectionError(f"{source_id} date window must be from 1 to 730 days")
            if not 1 <= source.get("max_results", 0) <= 100:
                raise CollectionError(f"{source_id} max_results must be from 1 to 100")
    enabled_sources = [
        source for source in registry["sources"] if source.get("enabled") is True
    ]
    if not enabled_sources:
        raise CollectionError("source registry contains no enabled sources")
    return enabled_sources


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"state_version": 1, "items": [], "latest_run": None}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CollectionError(f"could not read previous candidate state: {error}") from error
    if state.get("state_version") != 1 or not isinstance(state.get("items"), list):
        raise CollectionError("previous candidate state has an unsupported shape")
    for item in state["items"]:
        validate_candidate(item)
    return state


def merge_candidate(existing: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    """Idempotently merge location groups and tags when an event matches multiple queries."""
    combined_groups = set(existing["location_groups"]) | set(incoming["location_groups"])
    primary_location, ordered_groups = normalize_location_groups("other", combined_groups)
    combined_tags = sorted(set(existing["tags"]) | set(incoming["tags"]) | set(ordered_groups))
    merged = {
        **existing,
        "location": primary_location,
        "location_groups": ordered_groups,
        "tags": combined_tags,
    }
    validate_candidate(merged)
    return merged


def collect(
    *,
    sources_path: Path,
    state_path: Path,
    run_id: str,
    now: datetime | None = None,
) -> tuple[dict[str, Any], int]:
    run_time = now or utc_now()
    collected_at = iso_datetime(run_time)
    sources = load_sources(sources_path)
    state = load_state(state_path)
    by_id = {item["item_id"]: item for item in state["items"]}
    cutoff = (run_time - timedelta(days=RETENTION_DAYS)).date()
    by_id = {
        item_id: item
        for item_id, item in by_id.items()
        if date.fromisoformat(item["collected_at"][:10]) >= cutoff
    }
    source_results = []
    successful_sources = 0
    new_count = 0
    pubmed_calls = 0

    for source in sources:
        try:
            if source["source_type"] == "rss":
                payload = fetch_bytes(source["feed_url"])
                candidates = parse_rss(source, payload, collected_at, run_id)
            else:
                if pubmed_calls > 0:
                    time.sleep(0.4)
                pubmed_calls += 1
                candidates = fetch_pubmed(source, collected_at, run_id)
            successful_sources += 1
            source_new_count = 0
            for candidate in candidates:
                item_id = candidate["item_id"]
                if item_id not in by_id:
                    by_id[item_id] = candidate
                    source_new_count += 1
                    new_count += 1
                else:
                    by_id[item_id] = merge_candidate(by_id[item_id], candidate)
            source_results.append(
                {
                    "source_id": source["source_id"],
                    "status": "success",
                    "fetched": len(candidates),
                    "new": source_new_count,
                }
            )
        except CollectionError as error:
            source_results.append(
                {
                    "source_id": source["source_id"],
                    "status": "failed",
                    "error": f"{type(error).__name__}: {str(error)[:240]}",
                }
            )

    run_status = (
        "failed"
        if successful_sources == 0 and sources
        else "partial"
        if successful_sources < len(sources)
        else "success"
    )
    result = {
        "state_version": 1,
        "latest_run": {
            "run_id": run_id,
            "started_at": collected_at,
            "status": run_status,
            "sources_succeeded": successful_sources,
            "sources_total": len(sources),
            "new_candidates": new_count,
            "source_results": source_results,
        },
        "items": sorted(
            by_id.values(),
            key=lambda item: (
                item.get("publication_date") or "",
                item["item_id"],
            ),
            reverse=True,
        ),
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_summary(result["latest_run"])
    return result, successful_sources


def write_summary(run: dict[str, Any]) -> None:
    lines = [
        "## Longevity-events collection",
        "",
        f"- Run: `{run['run_id']}`",
        f"- Started (UTC): `{run['started_at']}`",
        f"- Status: **{run['status']}**",
        f"- Sources: {run['sources_succeeded']}/{run['sources_total']} succeeded",
        f"- New candidates: {run['new_candidates']}",
        "",
        "| Source | Status | Fetched | New |",
        "| --- | --- | ---: | ---: |",
    ]
    for source in run["source_results"]:
        lines.append(
            f"| `{source['source_id']}` | {source['status']} | "
            f"{source.get('fetched', '—')} | {source.get('new', '—')} |"
        )
    failures = [
        source for source in run["source_results"] if source["status"] == "failed"
    ]
    if failures:
        lines.extend(["", "Source failures:"])
        for source in failures:
            lines.append(f"- `{source['source_id']}`: {source['error']}")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as summary:
            summary.write("\n".join(lines) + "\n")
    else:
        print("\n".join(lines))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", "local"))
    arguments = parser.parse_args(argv)

    try:
        result, successful_sources = collect(
            sources_path=arguments.sources,
            state_path=arguments.state,
            run_id=arguments.run_id,
        )
    except CollectionError as error:
        print(f"Collector configuration/state error: {error}", file=sys.stderr)
        return 2

    total_sources = result["latest_run"]["sources_total"]
    if successful_sources == 0 and total_sources:
        print("All configured sources failed; previous candidates were preserved.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
