import unittest
from pathlib import Path

from app.pricing import analyze_note, load_catalog


class PricingTests(unittest.TestCase):
    def test_analyzes_split_basket(self):
        catalog = load_catalog(Path("data/catalog.csv"))
        result = analyze_note("1 gal whole milk\n12 eggs\n2 lb chicken breast", catalog)

        self.assertEqual(result["item_count"], 3)
        self.assertEqual(result["matched_count"], 3)
        self.assertGreater(result["split_total"], 0)
        self.assertEqual(result["missing"], [])
        self.assertIsNotNone(result["items"][0]["best_offer"]["price_per_serving"])


if __name__ == "__main__":
    unittest.main()

