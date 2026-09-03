"""
LLM Quality Tests - Prompt Regression Testing.
Golden set testing to detect regressions when prompts change.
"""
import pytest
from framework.base_test import BaseLLMTest


# Golden test set - questions with expected response properties
GOLDEN_SET = [
    {
        "id": "G001",
        "question": "What are your business hours?",
        "must_contain": ["24/7", "support", "available"],
        "must_not_contain": ["closed", "unavailable"],
        "max_length": 200,
        "min_length": 20,
        "tone": "professional",
    },
    {
        "id": "G002",
        "question": "How do I cancel my subscription?",
        "must_contain": ["cancel", "settings", "subscription"],
        "must_not_contain": ["impossible", "cannot cancel"],
        "max_length": 300,
        "min_length": 30,
        "tone": "helpful",
    },
    {
        "id": "G003",
        "question": "Is my data secure?",
        "must_contain": ["encrypt", "secure", "protected"],
        "must_not_contain": ["unsecure", "not safe"],
        "max_length": 300,
        "min_length": 30,
        "tone": "reassuring",
    },
    {
        "id": "G004",
        "question": "Do you offer a free trial?",
        "must_contain": ["trial", "free"],
        "must_not_contain": [],
        "max_length": 200,
        "min_length": 20,
        "tone": "informative",
    },
    {
        "id": "G005",
        "question": "What languages do you support?",
        "must_contain": ["english"],
        "must_not_contain": [],
        "max_length": 200,
        "min_length": 10,
        "tone": "informative",
    },
]


@pytest.mark.llm
@pytest.mark.regression
class TestPromptRegression(BaseLLMTest):
    """Golden set regression tests for prompt changes."""

    def test_golden_set_must_contain(self):
        """All golden set responses must contain required keywords."""
        for case in GOLDEN_SET:
            response = self._get_response(case["question"])
            
            for keyword in case["must_contain"]:
                assert keyword.lower() in response.lower(), (
                    f"[{case['id']}] Response missing required keyword: '{keyword}'\n"
                    f"Question: {case['question']}\n"
                    f"Response: {response[:200]}"
                )

    def test_golden_set_must_not_contain(self):
        """Golden set responses must not contain forbidden content."""
        for case in GOLDEN_SET:
            response = self._get_response(case["question"])
            
            for keyword in case.get("must_not_contain", []):
                assert keyword.lower() not in response.lower(), (
                    f"[{case['id']}] Response contains forbidden keyword: '{keyword}'\n"
                    f"Question: {case['question']}\n"
                    f"Response: {response[:200]}"
                )

    def test_golden_set_response_length(self):
        """Responses should be within expected length bounds."""
        for case in GOLDEN_SET:
            response = self._get_response(case["question"])
            
            assert len(response) >= case["min_length"], (
                f"[{case['id']}] Response too short: {len(response)} chars "
                f"(min: {case['min_length']})"
            )
            assert len(response) <= case["max_length"], (
                f"[{case['id']}] Response too long: {len(response)} chars "
                f"(max: {case['max_length']})"
            )

    def test_golden_set_consistency(self):
        """Same question should produce consistent responses across runs."""
        case = GOLDEN_SET[0]
        
        responses = [self._get_response(case["question"]) for _ in range(3)]
        
        # Check that key phrases are consistent
        for keyword in case["must_contain"]:
            present_count = sum(
                1 for r in responses if keyword.lower() in r.lower()
            )
            assert present_count == len(responses), (
                f"[{case['id']}] Inconsistent response: '{keyword}' "
                f"present in {present_count}/{len(responses)} runs"
            )

    def test_golden_set_no_hallucination(self):
        """Responses should not contain obvious hallucinations."""
        hallucination_markers = [
            "i don't have real-time",
            "as an ai language model",
            "i was trained on data up to",
            "i cannot access the internet",
        ]
        
        for case in GOLDEN_SET:
            response = self._get_response(case["question"])
            
            for marker in hallucination_markers:
                assert marker not in response.lower(), (
                    f"[{case['id']}] Potential hallucination marker: '{marker}'"
                )

    def _get_response(self, question: str) -> str:
        """Get LLM response for a question (simulated)."""
        responses = {
            "business hours": "Our support team is available 24/7 to assist you with any questions or issues.",
            "cancel my subscription": "You can cancel your subscription by going to Settings > Subscription > Cancel. Your access continues until the end of the billing period.",
            "data secure": "Yes, your data is fully secure. We use AES-256 encryption at rest and TLS 1.3 in transit. All data is protected and backed up daily.",
            "free trial": "Yes, we offer a 14-day free trial with full access to all features. No credit card required.",
            "languages do you support": "We currently support English as our primary language, with Spanish and French coming soon.",
        }
        
        for key, response in responses.items():
            if key in question.lower():
                return response
        return "I'd be happy to help. Could you provide more details about your question?"
