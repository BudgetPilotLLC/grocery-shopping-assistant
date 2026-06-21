from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
import re
import string
from typing import Iterable


UNIT_ALIASES = {
    "pound": "lb",
    "pounds": "lb",
    "lbs": "lb",
    "lb": "lb",
    "ounce": "oz",
    "ounces": "oz",
    "oz": "oz",
    "fl ounce": "fl_oz",
    "fl ounces": "fl_oz",
    "fluid ounce": "fl_oz",
    "fluid ounces": "fl_oz",
    "fl oz": "fl_oz",
    "floz": "fl_oz",
    "gallon": "gal",
    "gallons": "gal",
    "gal": "gal",
    "quart": "qt",
    "quarts": "qt",
    "qt": "qt",
    "pint": "pt",
    "pints": "pt",
    "pt": "pt",
    "cup": "cup",
    "cups": "cup",
    "count": "ct",
    "counts": "ct",
    "ct": "ct",
    "each": "ct",
    "ea": "ct",
    "dozen": "dozen",
    "doz": "dozen",
    "gram": "g",
    "grams": "g",
    "g": "g",
    "kilogram": "kg",
    "kilograms": "kg",
    "kg": "kg",
    "bag": "bag",
    "bags": "bag",
    "box": "box",
    "boxes": "box",
    "bunch": "bunch",
    "bunches": "bunch",
    "can": "can",
    "cans": "can",
    "jar": "jar",
    "jars": "jar",
    "loaf": "loaf",
    "loaves": "loaf",
    "pack": "pack",
    "packs": "pack",
    "package": "pack",
    "packages": "pack",
    "pkg": "pack",
    "item": "item",
}

NUMBER_WORDS = {
    "a": 1.0,
    "an": 1.0,
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "four": 4.0,
    "five": 5.0,
    "six": 6.0,
    "seven": 7.0,
    "eight": 8.0,
    "nine": 9.0,
    "ten": 10.0,
    "twelve": 12.0,
}

UNIT_PATTERN = "|".join(
    re.escape(unit)
    for unit in sorted(UNIT_ALIASES, key=len, reverse=True)
)

LEADING_MARKER_RE = re.compile(
    r"^\s*(?:[-*+]|[0-9]+[.)]|[a-zA-Z][.)]|\[\s?\]|\[[xX]\]|☐|☑|✓|•)\s*"
)
SERVING_RE = re.compile(
    r"\(?\b(?:serves|servings?|feeds)\s*:?\s*(?P<servings>\d+(?:\.\d+)?)\b\)?",
    re.IGNORECASE,
)
TRAILING_NOTES_RE = re.compile(r"\s+#.*$")
MULTISPACE_RE = re.compile(r"\s+")


@dataclass
class GroceryItem:
    line: str
    name: str
    quantity: float
    unit: str
    servings_requested: float | None = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["quantity_label"] = quantity_label(self.quantity, self.unit)
        return data


def parse_note_text(text: str) -> list[GroceryItem]:
    return [item for item in (parse_line(line) for line in text.splitlines()) if item]


def parse_line(line: str) -> GroceryItem | None:
    original = line.strip()
    cleaned = clean_line(original)
    if not cleaned or looks_like_heading(cleaned):
        return None

    servings = None
    serving_match = SERVING_RE.search(cleaned)
    if serving_match:
        servings = float(serving_match.group("servings"))
        cleaned = SERVING_RE.sub("", cleaned).strip(" -;")

    quantity, unit, name = parse_quantity_name(cleaned)
    name = normalize_display_name(name)
    if not name:
        return None

    return GroceryItem(
        line=original,
        name=name,
        quantity=quantity,
        unit=unit,
        servings_requested=servings,
    )


def clean_line(line: str) -> str:
    line = line.strip()
    line = LEADING_MARKER_RE.sub("", line)
    line = TRAILING_NOTES_RE.sub("", line)
    line = line.strip()
    if line.lower().startswith("todo:"):
        line = line[5:].strip()
    return line


def looks_like_heading(line: str) -> bool:
    if line.endswith(":") and len(line.split()) <= 4:
        return True
    lowered = line.lower()
    return lowered in {"groceries", "grocery list", "shopping list", "costco", "sams", "sam's", "aldi", "publix", "amazon"}


def parse_quantity_name(text: str) -> tuple[float, str, str]:
    trailing_x = re.match(r"^(?P<name>.+?)\s+[xX]\s*(?P<qty>\d+(?:\.\d+)?|\d+\s*/\s*\d+)$", text)
    if trailing_x:
        return parse_number(trailing_x.group("qty")), "ct", trailing_x.group("name")

    leading = re.match(
        rf"^(?P<qty>\d+(?:\.\d+)?|\d+\s*/\s*\d+|{'|'.join(NUMBER_WORDS)})\s*(?P<unit>{UNIT_PATTERN})?\b\s*(?P<name>.+)$",
        text,
        re.IGNORECASE,
    )
    if leading:
        qty = parse_number(leading.group("qty"))
        unit = normalize_unit(leading.group("unit") or "item")
        name = leading.group("name")
        if unit == "dozen":
            qty *= 12
            unit = "ct"
        return qty, unit, name

    return 1.0, "item", text


def parse_number(value: str) -> float:
    value = value.strip().lower()
    if value in NUMBER_WORDS:
        return NUMBER_WORDS[value]
    if "/" in value:
        return float(Fraction(value.replace(" ", "")))
    return float(value)


def normalize_unit(unit: str) -> str:
    return UNIT_ALIASES.get(unit.strip().lower(), unit.strip().lower().replace(" ", "_"))


def normalize_display_name(value: str) -> str:
    value = value.strip().strip("-:;,.")
    value = re.sub(r"\([^)]*\)", "", value)
    value = MULTISPACE_RE.sub(" ", value)
    return value.strip()


def tokenize(value: str) -> set[str]:
    lowered = value.lower()
    cleaned = lowered.translate(str.maketrans({char: " " for char in string.punctuation}))
    tokens = {token for token in cleaned.split() if len(token) > 1}
    return tokens - {
        "the",
        "and",
        "for",
        "with",
        "fresh",
        "plain",
        "large",
        "small",
        "medium",
        "oz",
        "lb",
        "lbs",
        "ct",
    }


def quantity_label(quantity: float, unit: str) -> str:
    pretty_qty = str(int(quantity)) if quantity == int(quantity) else f"{quantity:g}"
    if unit == "item":
        return pretty_qty
    return f"{pretty_qty} {unit.replace('_', ' ')}"


def items_to_dicts(items: Iterable[GroceryItem]) -> list[dict]:
    return [item.to_dict() for item in items]

