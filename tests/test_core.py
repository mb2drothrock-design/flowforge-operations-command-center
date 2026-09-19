import unittest

from flowforge.core import analyze_intake, classify_category, priority_label, score_priority


class CoreTests(unittest.TestCase):
    def test_support_classification_and_critical_priority(self):
        text = "CRITICAL outage. Checkout is down and all orders are blocked immediately."
        category = classify_category(text)
        score = score_priority(text, category)
        self.assertEqual(category, "support")
        self.assertGreaterEqual(score, 80)
        self.assertEqual(priority_label(score), "P0 - Critical")

    def test_billing_extraction(self):
        result = analyze_intake(
            "Email",
            "Duplicate charge",
            "Charged twice for invoice INV-55391 totaling $1,249.00. Email me at billing@example.com.",
        )
        self.assertEqual(result.category, "billing")
        self.assertIn("$1,249.00", result.monetary_values)
        self.assertIn("billing@example.com", result.emails)
        self.assertIn("INV-55391", result.reference_ids)

    def test_sales_routing(self):
        result = analyze_intake("Web", "Pricing request", "Need pricing and a demo for our team.")
        self.assertEqual(result.category, "sales")
        self.assertEqual(result.suggested_owner, "Revenue Operations")


if __name__ == "__main__":
    unittest.main()
