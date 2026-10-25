import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from events import collector


NATURE_EVENTS_SOURCE = {
    "source_id": "nature_aging_events",
    "name": "Nature Aging Conferences & Symposia",
    "publisher": "Springer Nature",
    "source_type": "rss",
    "format": "rss1",
    "topic_coverage": ["aging conferences"],
    "update_cadence": "daily",
    "permitted_collection_method": "public metadata feed",
    "terms_notes": "Metadata only.",
    "terms_url": "https://www.nature.com/info/terms-and-conditions",
    "trust_tier": "primary_publisher",
    "last_checked_date": "2026-10-25",
    "allowed_domains": ["nature.com"],
    "feed_url": "https://www.nature.com/nataging.rss",
    "filter_terms": ["conference", "symposium", "congress", "workshop", "forum"],
}

RSS_SAMPLE = b"""<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:rss="http://purl.org/rss/1.0/"
 xmlns:dc="http://purl.org/dc/elements/1.1/">
  <rss:item rdf:about="https://www.nature.com/articles/vienna-symposium?utm_source=feed">
    <rss:title>6th International Longevity Symposium in Vienna, Austria</rss:title>
    <rss:link>https://www.nature.com/articles/vienna-symposium?utm_source=feed</rss:link>
    <dc:date>2026-10-20</dc:date>
    <dc:creator>Example Organizer</dc:creator>
  </rss:item>
  <rss:item rdf:about="https://www.nature.com/articles/non-event">
    <rss:title>Cellular senescence mechanisms in mice</rss:title>
    <rss:link>https://www.nature.com/articles/non-event</rss:link>
  </rss:item>
  <rss:item rdf:about="https://outside.example/event">
    <rss:title>Off-domain conference</rss:title>
    <rss:link>https://outside.example/event</rss:link>
  </rss:item>
</rdf:RDF>"""


class LocationClassificationTests(unittest.TestCase):
    def test_vienna_event_includes_both_vienna_and_europe(self):
        location, groups, tags = collector.classify_location(
            "61st EASD Annual Meeting: Vienna, Austria"
        )
        self.assertEqual(location, "vienna")
        self.assertEqual(groups, ["vienna", "europe"])
        self.assertIn("vienna", tags)
        self.assertIn("europe", tags)
        self.assertIn("meeting", tags)

    def test_disambiguates_vienna_virginia_as_us(self):
        location, groups, _ = collector.classify_location(
            "Healthy Aging Community Workshop in Vienna, Virginia"
        )
        self.assertEqual(location, "us")
        self.assertEqual(groups, ["us"])

    def test_classifies_europe_us_asia_and_other(self):
        self.assertEqual(
            collector.classify_location("21st EuGMS Congress in Reykjavik")[0:2],
            ("europe", ["europe"]),
        )
        self.assertEqual(
            collector.classify_location("National Institute on Aging Workshop in Bethesda")[0:2],
            ("us", ["us"]),
        )
        self.assertEqual(
            collector.classify_location("TimePie Longevity Forum in Shanghai, China")[0:2],
            ("asia", ["asia"]),
        )
        self.assertEqual(
            collector.classify_location("Multidisciplinary Gerontological Symposium")[0:2],
            ("other", []),
        )

    def test_multi_region_title_preserves_all_matched_groups(self):
        location, groups, _ = collector.classify_location(
            "Presented at ECR Vienna, Austria and KSIR Busan, Korea"
        )
        self.assertEqual(location, "vienna")
        self.assertEqual(groups, ["vienna", "europe", "asia"])

    def test_uses_default_location_when_title_has_no_explicit_city(self):
        location, groups, _ = collector.classify_location(
            "International Workshop on Clinical Nutrition",
            default_location="vienna",
        )
        self.assertEqual(location, "vienna")
        self.assertEqual(groups, ["vienna", "europe"])


class EventParserTests(unittest.TestCase):
    def test_parses_rss_and_filters_to_event_items(self):
        candidates = collector.parse_rss(
            NATURE_EVENTS_SOURCE,
            RSS_SAMPLE,
            "2026-10-25T05:47:00Z",
            "test-run",
        )
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate["location"], "vienna")
        self.assertEqual(candidate["location_groups"], ["vienna", "europe"])
        self.assertEqual(
            candidate["source_url"],
            "https://www.nature.com/articles/vienna-symposium",
        )
        self.assertEqual(candidate["review_state"], "candidate")
        self.assertIsNone(candidate["summary"])

    def test_merges_duplicate_candidates_across_regional_and_global_queries(self):
        global_source = {**NATURE_EVENTS_SOURCE, "source_id": "global_src"}
        vienna_source = {
            **NATURE_EVENTS_SOURCE,
            "source_id": "vienna_src",
            "default_location": "vienna",
        }
        first = collector.build_candidate(
            source=global_source,
            upstream_id="1",
            title="Annual Longevity Congress Abstracts",
            article_url="https://www.nature.com/articles/congress-1",
            publication_date="2026-10-20",
            author=None,
            collected_at="2026-10-25T05:47:00Z",
            run_id="r1",
            access_basis="public_feed_metadata",
        )
        second = collector.build_candidate(
            source=vienna_source,
            upstream_id="1",
            title="Annual Longevity Congress Abstracts",
            article_url="https://www.nature.com/articles/congress-1",
            publication_date="2026-10-20",
            author=None,
            collected_at="2026-10-25T05:47:00Z",
            run_id="r1",
            access_basis="public_feed_metadata",
        )
        merged = collector.merge_candidate(first, second)
        self.assertEqual(merged["location"], "vienna")
        self.assertEqual(merged["location_groups"], ["vienna", "europe"])


class EventCollectionTests(unittest.TestCase):
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

    def test_partial_failure_and_idempotent_rerun(self):
        second_source = {**NATURE_EVENTS_SOURCE, "source_id": "nature_aging_events_2"}
        self.write_registry([NATURE_EVENTS_SOURCE, second_source])
        now = datetime(2026, 10, 25, 5, 47, tzinfo=timezone.utc)
        original_parse = collector.parse_rss

        def side_effect(source, *args):
            if source["source_id"] == "nature_aging_events_2":
                raise collector.CollectionError("feed timeout")
            return original_parse(source, *args)

        with patch.object(collector, "fetch_bytes", return_value=RSS_SAMPLE), patch.object(
            collector, "parse_rss", side_effect=side_effect
        ):
            first, count = collector.collect(
                sources_path=self.registry,
                state_path=self.state,
                run_id="run-1",
                now=now,
            )
        self.assertEqual(count, 1)
        self.assertEqual(first["latest_run"]["status"], "partial")
        self.assertEqual(len(first["items"]), 1)

        with patch.object(collector, "fetch_bytes", return_value=RSS_SAMPLE), patch.object(
            collector, "parse_rss", side_effect=side_effect
        ):
            second, _ = collector.collect(
                sources_path=self.registry,
                state_path=self.state,
                run_id="run-2",
                now=now,
            )
        self.assertEqual(second["latest_run"]["new_candidates"], 0)
        self.assertEqual(len(second["items"]), 1)


if __name__ == "__main__":
    unittest.main()
