import unittest

from app.parser import parse_note_text


class ParserTests(unittest.TestCase):
    def test_parses_common_grocery_lines(self):
        items = parse_note_text(
            """
            Groceries:
            - 2 lb chicken breast
            - milk x2
            - 12 eggs
            - rice (servings 10)
            """
        )

        self.assertEqual([item.name for item in items], ["chicken breast", "milk", "eggs", "rice"])
        self.assertEqual(items[0].quantity, 2)
        self.assertEqual(items[0].unit, "lb")
        self.assertEqual(items[1].quantity, 2)
        self.assertEqual(items[1].unit, "ct")
        self.assertEqual(items[3].servings_requested, 10)


if __name__ == "__main__":
    unittest.main()

