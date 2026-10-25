import hashlib
import unittest
from unittest.mock import AsyncMock, patch

from events import summarizer


def make_candidate(location="vienna"):
    groups = ["vienna", "europe"] if location == "vienna" else ([location] if location != "other" else [])
    return {
        "schema_version": 1,
        "item_id": hashlib.sha256(b"https://example.org/event").hexdigest(),
        "source_id": "test_source",
        "source_record_id": "event-1",
        "title": "Vienna Longevity Symposium 2026",
        "publisher": "Example Society",
        "author": "A. Organizer",
        "source_url": "https://example.org/event",
        "publication_date": "2026-10-20",
        "publication_date_precision": "day",
        "publication_date_raw": "2026-10-20",
        "collected_at": "2026-10-25T05:47:00Z",
        "content_access_basis": "public_feed_metadata",
        "location": location,
        "location_groups": groups,
        "location_method": "rules_candidate",
        "tags": ["needs_review", "symposium", *groups],
        "summary": None,
        "evidence_notes": None,
        "review_state": "candidate",
        "run_id": "collect-1",
        "last_updated": "2026-10-25T05:47:00Z",
    }


def make_model_output(**overrides):
    result = {
        "title": "Vienna Longevity Symposium 2026",
        "location": "vienna",
        "location_groups": ["vienna", "europe"],
        "tags": ["symposium", "geroscience"],
        "summary": "Researchers and clinicians convene in Vienna to discuss biomarkers of aging.",
        "key_points": [
            {
                "text": "Hosted in Vienna, Austria with sessions on biomarkers.",
                "source_paragraphs": [0],
            }
        ],
        "evidence_notes": "Academic symposium announcement; no clinical recommendations.",
        "confidence": 0.88,
        "risk_flags": [],
        "editorial_status": "approved",
        "editorial_reasons": [],
    }
    result.update(overrides)
    return result


class EventsSummarizerTests(unittest.TestCase):
    def test_vienna_output_normalizes_europe_into_location_groups(self):
        candidate = make_candidate("vienna")
        output = make_model_output(location="vienna", location_groups=["vienna"])
        result = summarizer.validate_model_output(output, candidate, 1)
        self.assertEqual(result["location"], "vienna")
        self.assertEqual(result["location_groups"], ["vienna", "europe"])
        self.assertEqual(result["editorial_status"], "approved")

    def test_promotional_event_requires_human_review(self):
        candidate = make_candidate("us")
        output = make_model_output(
            location="us",
            location_groups=["us"],
            risk_flags=["promotional_claim"],
        )
        result = summarizer.validate_model_output(output, candidate, 1)
        self.assertEqual(result["editorial_status"], "needs_review")


class EventsBatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_metadata_only_candidates_are_withheld_from_auto_summary(self):
        candidate = make_candidate("europe")
        with patch(
            "events.summarizer.call_antigravity", new_callable=AsyncMock
        ) as provider:
            records, audit = await summarizer.summarize_candidates(
                [candidate], {}, api_key="", model=None, run_id="run-1"
            )
        provider.assert_not_awaited()
        self.assertEqual(records[0]["editorial_status"], "needs_review")
        self.assertIsNone(records[0]["summary"])
        self.assertEqual(audit[0]["reason"], "no_authorized_source_text")
        summarizer.validate_record(records[0])


if __name__ == "__main__":
    unittest.main()
