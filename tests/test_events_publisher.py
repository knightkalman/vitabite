import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

from events import collector
from events.publish_metadata import build_public_feed, publish


class EventsMetadataPublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.sources_path = Path("events/sources.json")
        self.sources = collector.load_sources(self.sources_path)
        self.source = self.sources[0]
        self.candidate = collector.build_candidate(
            source=self.source,
            upstream_id="vienna-1",
            title="Longevity Congress in Vienna, Austria",
            article_url=f"https://{self.source['allowed_domains'][0]}/articles/vienna-1",
            publication_date="2026-10-20",
            author=None,
            collected_at="2026-10-25T05:47:00Z",
            run_id="test-run",
            access_basis="public_feed_metadata",
        )
        self.state = {
            "state_version": 1,
            "latest_run": {
                "run_id": "test-run",
                "started_at": "2026-10-25T05:47:00Z",
                "status": "success",
                "sources_succeeded": len(self.sources),
                "sources_total": len(self.sources),
                "new_candidates": 1,
                "source_results": [
                    {
                        "source_id": source["source_id"],
                        "status": "success",
                        "fetched": 1,
                        "new": 1,
                    }
                    for source in self.sources
                ],
            },
            "items": [self.candidate],
        }

    def test_publishes_schema_valid_public_events_feed(self):
        feed = build_public_feed(
            self.state,
            self.sources,
            generated_at=datetime(2026, 10, 25, tzinfo=timezone.utc),
        )
        schema = json.loads(
            Path("events/schemas/public-feed.schema.json").read_text(encoding="utf-8")
        )
        jsonschema.validate(feed, schema, format_checker=jsonschema.FormatChecker())
        self.assertEqual(feed["publication_status"], "metadata_roundup")
        self.assertEqual(len(feed["items"]), 1)
        item = feed["items"][0]
        self.assertEqual(item["location"], "vienna")
        self.assertEqual(item["location_groups"], ["vienna", "europe"])
        self.assertEqual(item["review_state"], "candidate")
        self.assertIsNone(item["summary"])

    def test_failed_run_does_not_overwrite_existing_feed(self):
        state_path = self.root / "candidates.json"
        output_path = self.root / "events.json"
        state_path.write_text(
            json.dumps(
                {
                    **self.state,
                    "latest_run": {
                        **self.state["latest_run"],
                        "status": "failed",
                        "sources_succeeded": 0,
                    },
                }
            ),
            encoding="utf-8",
        )
        output_path.write_text('{"previous":true}\n', encoding="utf-8")
        with self.assertRaises(collector.CollectionError):
            publish(
                state_path=state_path,
                sources_path=self.sources_path,
                output_path=output_path,
            )
        self.assertEqual(output_path.read_text(encoding="utf-8"), '{"previous":true}\n')


if __name__ == "__main__":
    unittest.main()
