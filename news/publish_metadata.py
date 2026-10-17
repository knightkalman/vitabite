"""Publish collector metadata headlines to the static news feed."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from news.collector import CollectionError, iso_datetime, load_sources, validate_candidate

ROOT = Path(__file__).resolve().parent.parent


def project_candidate(
    candidate: dict[str, Any], enabled_sources: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    validate_candidate(candidate)
    source = enabled_sources.get(candidate["source_id"])
    if source is None:
        raise CollectionError("candidate source is not currently enabled")
    host = (urlsplit(candidate["source_url"]).hostname or "").lower()
    if not any(
        host == domain or host.endswith("." + domain)
        for domain in source["allowed_domains"]
    ):
        raise CollectionError("candidate article URL is outside its source allowlist")
    if candidate["summary"] is not None or candidate["evidence_notes"] is not None:
        raise CollectionError("metadata-only publication cannot include generated summaries")

    return {
        "item_id": candidate["item_id"],
        "title": candidate["title"],
        "publisher": candidate["publisher"],
        "author": candidate["author"],
        "source_url": candidate["source_url"],
        "publication_date": candidate["publication_date"],
        "publication_date_precision": candidate["publication_date_precision"],
        "publication_date_raw": candidate["publication_date_raw"],
        "category": candidate["category"],
        "tags": candidate["tags"],
        "summary": None,
        "evidence_notes": None,
        "review_state": "candidate",
    }


def build_public_feed(
    state: dict[str, Any],
    sources: list[dict[str, Any]],
    *,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    latest_run = state.get("latest_run")
    if not isinstance(latest_run, dict):
        raise CollectionError("collector state has no latest run")
    status = latest_run.get("status")
    if status not in {"success", "partial"}:
        raise CollectionError("only successful or partial collector runs may be published")
    if latest_run.get("sources_succeeded", 0) < 1:
        raise CollectionError("collector run has no successful sources")
    if latest_run.get("sources_total", 0) < latest_run["sources_succeeded"]:
        raise CollectionError("collector source counts are invalid")
    if not isinstance(state.get("items"), list):
        raise CollectionError("collector state has no candidate list")

    enabled_sources = {source["source_id"]: source for source in sources}
    items_by_id: dict[str, dict[str, Any]] = {}
    for candidate in state["items"]:
        if candidate.get("source_id") not in enabled_sources:
            continue
        item = project_candidate(candidate, enabled_sources)
        if item["item_id"] in items_by_id:
            raise CollectionError("collector state contains duplicate item IDs")
        items_by_id[item["item_id"]] = item

    run_timestamp = latest_run.get("started_at")
    try:
        datetime.fromisoformat(run_timestamp.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as error:
        raise CollectionError("collector run timestamp is invalid") from error
    generated_time = generated_at or datetime.now(timezone.utc)
    source_results = latest_run.get("source_results")
    if not isinstance(source_results, list):
        raise CollectionError("collector source results are missing")
    if len(source_results) != latest_run["sources_total"]:
        raise CollectionError("collector source result count is inconsistent")
    public_source_results = []
    for result in source_results:
        if not isinstance(result, dict) or result.get("source_id") not in enabled_sources:
            raise CollectionError("collector result contains an unknown source")
        public_result = {
            "source_id": result["source_id"],
            "status": result.get("status"),
        }
        if public_result["status"] not in {"success", "failed"}:
            raise CollectionError("collector result has an invalid source status")
        for field in ("fetched", "new"):
            if field in result:
                value = result[field]
                if not isinstance(value, int) or value < 0:
                    raise CollectionError("collector source counts must be non-negative integers")
                public_result[field] = value
        public_source_results.append(public_result)
    if sum(result["status"] == "success" for result in public_source_results) != latest_run[
        "sources_succeeded"
    ]:
        raise CollectionError("collector source success count is inconsistent")

    return {
        "schema_version": 1,
        "publication_status": "metadata_roundup",
        "generated_at": iso_datetime(generated_time),
        "last_successful_collection": run_timestamp,
        "collection_status": status,
        "sources_succeeded": latest_run["sources_succeeded"],
        "sources_total": latest_run["sources_total"],
        "source_results": public_source_results,
        "items": sorted(
            items_by_id.values(),
            key=lambda item: (
                item["publication_date"] or "",
                item["item_id"],
            ),
            reverse=True,
        ),
    }


def publish(
    *,
    state_path: Path,
    sources_path: Path,
    output_path: Path,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CollectionError(f"could not read candidate state: {error}") from error
    if state.get("state_version") != 1:
        raise CollectionError("candidate state version is unsupported")
    sources = load_sources(sources_path)
    feed = build_public_feed(state, sources, generated_at=generated_at)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(feed, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(output_path)
    return feed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--state",
        type=Path,
        default=ROOT / ".longevity-news-state" / "candidates.json",
    )
    parser.add_argument("--sources", type=Path, default=ROOT / "news" / "sources.json")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "public" / "news" / "news.json",
    )
    arguments = parser.parse_args(argv)
    try:
        feed = publish(
            state_path=arguments.state,
            sources_path=arguments.sources,
            output_path=arguments.output,
        )
    except CollectionError as error:
        print(f"News metadata publication failed: {error}", file=sys.stderr)
        return 1

    print(
        f"Published {len(feed['items'])} unreviewed headline(s); "
        f"collection status: {feed['collection_status']} "
        f"({feed['sources_succeeded']}/{feed['sources_total']} sources)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
