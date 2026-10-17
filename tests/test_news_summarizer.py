import hashlib
import unittest
from unittest.mock import AsyncMock, patch

from news import summarizer


def make_candidate(category="scientific"):
    return {
        "schema_version": 1,
        "item_id": hashlib.sha256(b"https://example.org/story").hexdigest(),
        "source_id": "test_source",
        "source_record_id": "story-1",
        "title": "A controlled study of healthy aging",
        "publisher": "Example Journal",
        "author": "A. Author",
        "source_url": "https://example.org/story",
        "publication_date": "2026-10-16",
        "publication_date_precision": "day",
        "publication_date_raw": "2026-10-16",
        "collected_at": "2026-10-17T05:17:00Z",
        "content_access_basis": "public_feed_metadata",
        "category": category,
        "category_method": "rules_candidate",
        "tags": ["needs_review", category],
        "summary": None,
        "evidence_notes": None,
        "review_state": "candidate",
        "run_id": "collect-1",
        "last_updated": "2026-10-17T05:17:00Z",
    }


def make_model_output(**overrides):
    result = {
        "title": "A controlled study of healthy aging",
        "category": "scientific",
        "tags": ["human_study", "observational"],
        "summary": "Researchers studied healthy aging in a defined population. "
        "The findings were observational and do not establish causation.",
        "key_points": [
            {
                "text": "The study was observational.",
                "source_paragraphs": [0],
            }
        ],
        "evidence_notes": "Observational findings; causal effects were not tested.",
        "confidence": 0.82,
        "risk_flags": [],
        "editorial_status": "approved",
        "editorial_reasons": [],
    }
    result.update(overrides)
    return result


class ContentBundleTests(unittest.TestCase):
    def test_requires_explicit_authorization_and_exact_source_url(self):
        candidate = make_candidate()
        entry = {
            "item_id": candidate["item_id"],
            "source_url": candidate["source_url"],
            "processing_authorized": True,
            "authorization_basis": "publisher_permission",
            "text": "Paragraph one.\n\nParagraph two.",
        }
        content = summarizer.validate_content_bundle(
            {"schema_version": 1, "items": [entry]}, [candidate]
        )
        self.assertEqual(content[candidate["item_id"]]["text"], entry["text"])

        for changes in (
            {"processing_authorized": False},
            {"source_url": "https://other.example/story"},
            {"authorization_basis": "unknown"},
        ):
            invalid = {**entry, **changes}
            with self.subTest(changes=changes), self.assertRaises(
                summarizer.SummarizerError
            ):
                summarizer.validate_content_bundle(
                    {"schema_version": 1, "items": [invalid]}, [candidate]
                )

    def test_rejects_duplicate_and_oversized_content(self):
        candidate = make_candidate()
        entry = {
            "item_id": candidate["item_id"],
            "source_url": candidate["source_url"],
            "processing_authorized": True,
            "authorization_basis": "licensed_excerpt",
            "text": "Text.",
        }
        with self.assertRaises(summarizer.SummarizerError):
            summarizer.validate_content_bundle(
                {"schema_version": 1, "items": [entry, entry]}, [candidate]
            )
        with self.assertRaises(summarizer.SummarizerError):
            summarizer.validate_content_bundle(
                {
                    "schema_version": 1,
                    "items": [
                        {**entry, "text": "x" * (summarizer.MAX_SOURCE_TEXT_CHARS + 1)}
                    ],
                },
                [candidate],
            )


class OutputSafetyTests(unittest.TestCase):
    def test_accepts_each_controlled_category(self):
        for category in summarizer.ALLOWED_CATEGORIES:
            with self.subTest(category=category):
                candidate = make_candidate(category)
                output = make_model_output(category=category)
                result = summarizer.validate_model_output(output, candidate, 1)
                self.assertIn(result["category"], summarizer.ALLOWED_CATEGORIES)

    def test_medication_requires_human_review_even_if_model_approves(self):
        candidate = make_candidate("medication")
        output = make_model_output(category="medication")
        result = summarizer.validate_model_output(output, candidate, 1)
        self.assertEqual(result["editorial_status"], "needs_review")
        self.assertTrue(result["editorial_reasons"])

    def test_mixed_medication_topic_cannot_bypass_review(self):
        candidate = make_candidate("scientific")
        output = make_model_output(category="medication")
        result = summarizer.validate_model_output(output, candidate, 1)
        self.assertEqual(result["editorial_status"], "needs_review")

    def test_promotional_and_preliminary_claims_require_review(self):
        for flag in (
            "promotional_claim",
            "preliminary_evidence",
            "preprint",
            "animal_or_in_vitro",
            "conflicting_evidence",
            "potential_medical_advice",
        ):
            with self.subTest(flag=flag):
                result = summarizer.validate_model_output(
                    make_model_output(risk_flags=[flag]), make_candidate(), 1
                )
                self.assertEqual(result["editorial_status"], "needs_review")

    def test_low_confidence_requires_review(self):
        result = summarizer.validate_model_output(
            make_model_output(confidence=0.4), make_candidate(), 1
        )
        self.assertEqual(result["editorial_status"], "needs_review")

    def test_invalid_schema_and_unsupported_citations_fail(self):
        with self.assertRaises(summarizer.SummarizerError):
            summarizer.validate_model_output(
                make_model_output(category="other"), make_candidate(), 1
            )
        with self.assertRaises(summarizer.SummarizerError):
            summarizer.validate_model_output(
                make_model_output(
                    key_points=[
                        {"text": "Unsupported point.", "source_paragraphs": [1]}
                    ]
                ),
                make_candidate(),
                1,
            )

    def test_inaccessible_candidate_has_no_invented_summary(self):
        record = summarizer.make_unprocessed_record(
            make_candidate(), "run-1", "withheld", "Source unavailable."
        )
        self.assertIsNone(record["summary"])
        self.assertEqual(record["editorial_status"], "withheld")
        summarizer.validate_record(record)


class BatchTests(unittest.IsolatedAsyncioTestCase):
    async def test_metadata_only_candidates_are_reviewed_without_provider_call(self):
        candidate = make_candidate()
        with patch(
            "news.summarizer.call_antigravity", new_callable=AsyncMock
        ) as provider:
            records, audit = await summarizer.summarize_candidates(
                [candidate], {}, api_key="", model=None, run_id="run-1"
            )
        provider.assert_not_awaited()
        self.assertEqual(records[0]["editorial_status"], "needs_review")
        self.assertIsNone(records[0]["summary"])
        self.assertEqual(audit[0]["reason"], "no_authorized_source_text")
        summarizer.validate_record(records[0])

    async def test_provider_failure_is_explicit_and_keeps_item_queued(self):
        candidate = make_candidate()
        content = {
            candidate["item_id"]: {
                "text": "Permitted source paragraph.",
                "authorization_basis": "licensed_excerpt",
            }
        }
        with patch(
            "news.summarizer.call_antigravity",
            new_callable=AsyncMock,
            side_effect=RuntimeError(
                "provider unavailable test-secret Permitted source paragraph."
            ),
        ):
            records, audit = await summarizer.summarize_candidates(
                [candidate], content, api_key="test-secret", model=None, run_id="run-1"
            )
        self.assertEqual(records[0]["editorial_status"], "needs_review")
        self.assertEqual(audit[0]["status"], "error")
        self.assertNotIn("test-secret", str(audit))
        self.assertNotIn("Permitted source paragraph.", str(audit))
        self.assertIn("details omitted", audit[0]["error"])
        summarizer.validate_record(records[0])


if __name__ == "__main__":
    unittest.main()
