import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from news import collector
from news.publish_metadata import build_public_feed, publish


class MetadataPublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.sources_path = Path("news/sources.json")
        self.sources = collector.load_sources(self.sources_path)
        self.source = self.sources[0]
        self.candidate = collector.build_candidate(
            source=self.source,
            upstream_id="example",
            title="A study of healthy aging",
            article_url=f"https://{self.source['allowed_domains'][0]}/articles/example",
            publication_date="2026-10-16",
            author=None,
            collected_at="2026-10-17T05:17:00Z",
            run_id="test-run",
            access_basis="public_feed_metadata",
        )
        self.state = {
            "state_version": 1,
            "latest_run": {
                "run_id": "test-run",
                "started_at": "2026-10-17T05:17:00Z",
                "status": "success",
                "sources_succeeded": 2,
                "sources_total": 2,
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

    def test_publishes_only_unreviewed_source_metadata(self):
        feed = build_public_feed(
            self.state,
            self.sources,
            generated_at=datetime(2026, 10, 17, tzinfo=timezone.utc),
        )
        self.assertEqual(feed["publication_status"], "metadata_roundup")
        self.assertEqual(feed["collection_status"], "success")
        self.assertEqual(len(feed["items"]), 1)
        item = feed["items"][0]
        self.assertEqual(item["review_state"], "candidate")
        self.assertIsNone(item["summary"])
        self.assertIsNone(item["evidence_notes"])
        self.assertEqual(
            set(item),
            {
                "item_id",
                "title",
                "publisher",
                "author",
                "source_url",
                "publication_date",
                "publication_date_precision",
                "publication_date_raw",
                "category",
                "tags",
                "summary",
                "evidence_notes",
                "review_state",
            },
        )

    def test_partial_run_is_marked_with_source_statuses(self):
        self.state["latest_run"]["status"] = "partial"
        self.state["latest_run"]["sources_succeeded"] = 1
        self.state["latest_run"]["source_results"][1]["status"] = "failed"
        feed = build_public_feed(self.state, self.sources)
        self.assertEqual(feed["collection_status"], "partial")
        self.assertEqual(feed["sources_succeeded"], 1)
        self.assertEqual(feed["source_results"][1]["status"], "failed")
        self.assertNotIn("error", feed["source_results"][1])

    def test_fully_failed_run_is_not_published(self):
        self.state["latest_run"]["status"] = "failed"
        self.state["latest_run"]["sources_succeeded"] = 0
        with self.assertRaises(collector.CollectionError):
            build_public_feed(self.state, self.sources)

    def test_inconsistent_source_results_are_rejected(self):
        self.state["latest_run"]["sources_succeeded"] = 1
        with self.assertRaises(collector.CollectionError):
            build_public_feed(self.state, self.sources)

    def test_disabled_source_and_off_domain_items_are_not_published(self):
        disabled_candidate = {
            **self.candidate,
            "source_id": "food_business_news",
        }
        feed = build_public_feed(
            {**self.state, "items": [disabled_candidate]},
            self.sources,
        )
        self.assertEqual(feed["items"], [])

        off_domain = {
            **self.candidate,
            "source_url": "https://example.org/article",
        }
        off_domain["item_id"] = collector.stable_id(off_domain["source_url"])
        with self.assertRaises(collector.CollectionError):
            build_public_feed(
                {**self.state, "items": [off_domain]},
                self.sources,
            )

    def test_failure_does_not_replace_previous_public_feed(self):
        state_path = self.root / "candidates.json"
        output_path = self.root / "news.json"
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

    def test_publish_writes_only_validated_public_projection(self):
        state_path = self.root / "candidates.json"
        sources_path = self.root / "sources.json"
        output_path = self.root / "public" / "news.json"
        state_path.write_text(json.dumps(self.state), encoding="utf-8")
        sources_path.write_text(
            json.dumps(
                {
                    "registry_version": 1,
                    "sources": self.sources,
                }
            ),
            encoding="utf-8",
        )
        feed = publish(
            state_path=state_path,
            sources_path=sources_path,
            output_path=output_path,
            generated_at=datetime(2026, 10, 17, tzinfo=timezone.utc),
        )
        saved = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(feed, saved)
        self.assertEqual(saved["publication_status"], "metadata_roundup")
        self.assertEqual(saved["items"][0]["review_state"], "candidate")
        self.assertIsNone(saved["items"][0]["summary"])


if __name__ == "__main__":
    unittest.main()
