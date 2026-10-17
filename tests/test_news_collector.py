import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from news import collector


NATURE_SOURCE = {
    "source_id": "nature_aging",
    "name": "Nature Aging",
    "publisher": "Springer Nature",
    "source_type": "rss",
    "format": "rss1",
    "topic_coverage": ["aging research"],
    "update_cadence": "daily",
    "permitted_collection_method": "public metadata feed",
    "terms_notes": "Metadata only.",
    "terms_url": "https://www.nature.com",
    "trust_tier": "primary_publisher",
    "last_checked_date": "2026-10-17",
    "allowed_domains": ["nature.com"],
    "feed_url": "https://www.nature.com/nataging.rss",
}
RSS_SAMPLE = b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:rss="http://purl.org/rss/1.0/"
 xmlns:dc="http://purl.org/dc/elements/1.1/">
  <rss:item rdf:about="https://www.nature.com/articles/example?utm_source=feed">
    <rss:title>Vitamin D and healthy aging</rss:title>
    <rss:link>https://www.nature.com/articles/example?utm_source=feed</rss:link>
    <dc:date>2026-10-16</dc:date>
    <dc:creator>Example Author</dc:creator>
  </rss:item>
  <rss:item rdf:about="https://outside.example/article">
    <rss:title>Off-domain record</rss:title>
    <rss:link>https://outside.example/article</rss:link>
  </rss:item>
</rdf:RDF>"""


class CanonicalizationTests(unittest.TestCase):
    def test_removes_tracking_and_fragment(self):
        actual = collector.canonicalize_url(
            "https://www.nature.com/articles/a/?utm_source=rss&x=1#abstract",
            ["nature.com"],
        )
        self.assertEqual(actual, "https://www.nature.com/articles/a?x=1")

    def test_rejects_non_https_credentials_and_unapproved_host(self):
        for url in (
            "http://www.nature.com/article",
            "https://user:pass@www.nature.com/article",
            "https://nature.com.attacker.example/article",
        ):
            with self.subTest(url=url), self.assertRaises(collector.CollectionError):
                collector.canonicalize_url(url, ["nature.com"])


class ParserTests(unittest.TestCase):
    def test_preserves_partial_publication_date_precision(self):
        self.assertEqual(
            collector.parse_publication_date("2026 Oct"),
            (None, "month", "2026 Oct"),
        )
        self.assertEqual(
            collector.parse_publication_date("2026"),
            (None, "year", "2026"),
        )
        self.assertEqual(
            collector.parse_publication_date("2026-10-16"),
            ("2026-10-16", "day", "2026-10-16"),
        )

    def test_parses_rss1_as_unsummarized_candidates(self):
        candidates = collector.parse_rss(
            NATURE_SOURCE,
            RSS_SAMPLE,
            "2026-10-17T05:17:00Z",
            "test-run",
        )
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate["category"], "nutrients")
        self.assertEqual(candidate["source_url"], "https://www.nature.com/articles/example")
        self.assertEqual(candidate["author"], "Example Author")
        self.assertEqual(candidate["review_state"], "candidate")
        self.assertIsNone(candidate["summary"])
        self.assertIsNone(candidate["evidence_notes"])

    def test_rss_title_filter_omits_unrelated_items(self):
        source = {**NATURE_SOURCE, "filter_terms": ["creatine"]}
        candidates = collector.parse_rss(
            source,
            RSS_SAMPLE,
            "2026-10-17T05:17:00Z",
            "test-run",
        )
        self.assertEqual(candidates, [])

    def test_pubmed_uses_journal_as_article_publisher(self):
        source = {
            **NATURE_SOURCE,
            "source_id": "pubmed_longevity",
            "source_type": "pubmed_eutils",
            "format": "json",
            "feed_url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
            "query": "longevity",
            "date_window_days": 30,
            "max_results": 50,
            "allowed_domains": ["pubmed.ncbi.nlm.nih.gov"],
        }
        search = json.dumps({"esearchresult": {"idlist": ["12345"]}}).encode()
        summary = json.dumps(
            {
                "result": {
                    "uids": ["12345"],
                    "12345": {
                        "title": "Aging cohort study",
                        "fulljournalname": "Journal of Healthy Aging",
                        "pubdate": "2026-10-16",
                        "authors": [{"name": "Example Researcher"}],
                    },
                }
            }
        ).encode()
        with patch.object(collector, "fetch_bytes", side_effect=[search, summary]):
            candidates = collector.fetch_pubmed(
                source,
                "2026-10-17T05:17:00Z",
                "test-run",
            )
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["publisher"], "Journal of Healthy Aging")
        self.assertEqual(
            candidates[0]["source_url"],
            "https://pubmed.ncbi.nlm.nih.gov/12345",
        )

    def test_classification_uses_specific_category_precedence(self):
        self.assertEqual(collector.classify("Metformin and vitamin D trial")[0], "medication")
        self.assertEqual(collector.classify("Supplement product launch")[0], "consumer_goods")
        self.assertEqual(
            collector.classify("Jimmybar formulates creatine-infused trail mix")[0],
            "consumer_goods",
        )
        self.assertEqual(collector.classify("Protein intake in healthy aging")[0], "nutrients")
        self.assertEqual(collector.classify("Aging cohort study")[0], "scientific")

    def test_invalid_feed_fails_explicitly(self):
        with self.assertRaises(collector.CollectionError):
            collector.parse_rss(NATURE_SOURCE, b"<broken", "2026-10-17T00:00:00Z", "r")


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        summary_patcher = patch.object(collector, "write_summary")
        summary_patcher.start()
        self.addCleanup(summary_patcher.stop)
        self.root = Path(self.temp_dir.name)
        self.registry = self.root / "sources.json"
        self.state = self.root / "state.json"

    def write_registry(self, sources):
        for source in sources:
            source.setdefault("enabled", True)
        self.registry.write_text(
            json.dumps({"registry_version": 1, "sources": sources}),
            encoding="utf-8",
        )

    def test_source_failure_does_not_hide_success_and_rerun_is_idempotent(self):
        second_source = {
            **NATURE_SOURCE,
            "source_id": "nature_aging_2",
        }
        self.write_registry([NATURE_SOURCE, second_source])
        now = datetime(2026, 10, 17, 5, 17, tzinfo=timezone.utc)

        parse_rss = collector.parse_rss

        def parse_source(source, *args):
            if source["source_id"] == "nature_aging_2":
                raise collector.CollectionError("temporary feed failure")
            return parse_rss(source, *args)

        with patch.object(collector, "fetch_bytes", return_value=RSS_SAMPLE), patch.object(
            collector, "parse_rss", side_effect=parse_source
        ):
            first, success_count = collector.collect(
                sources_path=self.registry,
                state_path=self.state,
                run_id="first",
                now=now,
            )
        self.assertEqual(success_count, 1)
        self.assertEqual(first["latest_run"]["status"], "partial")
        self.assertEqual(len(first["items"]), 1)

        with patch.object(collector, "fetch_bytes", return_value=RSS_SAMPLE), patch.object(
            collector, "parse_rss", side_effect=parse_source
        ):
            second, success_count = collector.collect(
                sources_path=self.registry,
                state_path=self.state,
                run_id="second",
                now=now,
            )
        self.assertEqual(success_count, 1)
        self.assertEqual(len(second["items"]), 1)
        self.assertEqual(second["latest_run"]["new_candidates"], 0)

    def test_all_source_failure_preserves_previous_state_and_reports_failure(self):
        self.write_registry([NATURE_SOURCE])
        previous = collector.build_candidate(
            source=NATURE_SOURCE,
            upstream_id="previous",
            title="A previous aging study",
            article_url="https://www.nature.com/articles/previous",
            publication_date="2026-10-10",
            author=None,
            collected_at="2026-10-11T00:00:00Z",
            run_id="previous-run",
            access_basis="public_feed_metadata",
        )
        self.state.write_text(
            json.dumps(
                {
                    "state_version": 1,
                    "items": [previous],
                    "latest_run": None,
                }
            ),
            encoding="utf-8",
        )
        with patch.object(
            collector,
            "fetch_bytes",
            side_effect=collector.CollectionError("feed unavailable"),
        ):
            result, success_count = collector.collect(
                sources_path=self.registry,
                state_path=self.state,
                run_id="failed",
                now=datetime(2026, 10, 17, tzinfo=timezone.utc),
            )
        self.assertEqual(success_count, 0)
        self.assertEqual(result["latest_run"]["status"], "failed")
        self.assertEqual(result["items"], [previous])
        self.assertIn("feed unavailable", result["latest_run"]["source_results"][0]["error"])

    def test_expired_candidates_are_pruned(self):
        self.write_registry([NATURE_SOURCE])
        old_time = "2026-09-01T00:00:00Z"
        candidate = collector.build_candidate(
            source=NATURE_SOURCE,
            upstream_id="old",
            title="Old aging study",
            article_url="https://www.nature.com/articles/old",
            publication_date="2026-08-30",
            author=None,
            collected_at=old_time,
            run_id="old-run",
            access_basis="public_feed_metadata",
        )
        self.state.write_text(
            json.dumps(
                {
                    "state_version": 1,
                    "items": [candidate],
                    "latest_run": None,
                }
            ),
            encoding="utf-8",
        )
        with patch.object(
            collector, "fetch_bytes", return_value=RSS_SAMPLE
        ), patch.object(collector, "parse_rss", return_value=[]):
            result, success_count = collector.collect(
                sources_path=self.registry,
                state_path=self.state,
                run_id="new",
                now=datetime(2026, 10, 17, tzinfo=timezone.utc),
            )
        self.assertEqual(success_count, 1)
        self.assertEqual(result["items"], [])

    def test_retry_has_bounded_attempts(self):
        with patch.object(
            collector.urllib.request,
            "urlopen",
            side_effect=TimeoutError("late"),
        ) as mocked_open, patch.object(collector.time, "sleep"):
            with self.assertRaises(collector.CollectionError):
                collector.fetch_bytes("https://www.nature.com/nataging.rss", attempts=2)
        self.assertEqual(mocked_open.call_count, 2)


if __name__ == "__main__":
    unittest.main()
