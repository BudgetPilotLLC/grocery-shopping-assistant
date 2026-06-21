from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
import math
from pathlib import Path
from statistics import mean
from typing import Iterable

from .parser import GroceryItem, normalize_unit, parse_note_text, tokenize


WEIGHT_TO_OZ = {
    "oz": 1.0,
    "lb": 16.0,
    "g": 0.03527396195,
    "kg": 35.27396195,
}

VOLUME_TO_FL_OZ = {
    "fl_oz": 1.0,
    "cup": 8.0,
    "pt": 16.0,
    "qt": 32.0,
    "gal": 128.0,
}

COUNT_UNITS = {"ct", "item", "pack", "bag", "box", "bunch", "can", "jar", "loaf"}
DEFAULT_STORES = ["Amazon", "Amazon Fresh", "Publix", "Aldi", "Sam's Club"]


@dataclass
class CatalogOffer:
    store: str
    product: str
    category: str
    aliases: list[str]
    size_qty: float
    size_unit: str
    package_desc: str
    price: float
    servings: float
    url: str
    last_updated: str
    zip: str
    notes: str

    @property
    def price_per_serving(self) -> float | None:
        if self.servings <= 0:
            return None
        return self.price / self.servings

    def to_dict(self) -> dict:
        data = asdict(self)
        data["price_per_serving"] = self.price_per_serving
        return data


@dataclass
class MatchedOffer:
    offer: CatalogOffer
    score: float
    package_count: int
    total_price: float

    def to_dict(self) -> dict:
        data = self.offer.to_dict()
        data.update(
            {
                "score": round(self.score, 3),
                "package_count": self.package_count,
                "total_price": round(self.total_price, 2),
                "price": round(self.offer.price, 2),
                "price_per_serving": (
                    round(self.offer.price_per_serving, 3)
                    if self.offer.price_per_serving is not None
                    else None
                ),
            }
        )
        return data


def load_catalog(path: Path) -> list[CatalogOffer]:
    if not path.exists():
        return []

    offers: list[CatalogOffer] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if not row.get("store") or not row.get("product"):
                continue
            offers.append(
                CatalogOffer(
                    store=row["store"].strip(),
                    product=row["product"].strip(),
                    category=row.get("category", "").strip(),
                    aliases=[part.strip() for part in row.get("aliases", "").split(";") if part.strip()],
                    size_qty=parse_float(row.get("size_qty"), 1.0),
                    size_unit=normalize_unit(row.get("size_unit", "item")),
                    package_desc=row.get("package_desc", "").strip(),
                    price=parse_float(row.get("price"), 0.0),
                    servings=parse_float(row.get("servings"), 0.0),
                    url=row.get("url", "").strip(),
                    last_updated=row.get("last_updated", "").strip(),
                    zip=row.get("zip", "").strip(),
                    notes=row.get("notes", "").strip(),
                )
            )
    return offers


def analyze_note(
    text: str,
    catalog: Iterable[CatalogOffer],
    stores: Iterable[str] | None = None,
    zip_code: str = "",
) -> dict:
    return analyze_items(parse_note_text(text), catalog, stores=stores, zip_code=zip_code)


def analyze_items(
    items: Iterable[GroceryItem],
    catalog: Iterable[CatalogOffer],
    stores: Iterable[str] | None = None,
    zip_code: str = "",
) -> dict:
    selected_stores = list(stores or DEFAULT_STORES)
    selected_store_set = set(selected_stores)
    all_offers = [offer for offer in catalog if offer.store in selected_store_set]

    item_results = []
    split_total = 0.0
    matched_count = 0

    for item in items:
        matches = sorted(
            (
                match_offer(item, offer)
                for offer in all_offers
            ),
            key=lambda match: (-match.score, match.total_price, match.offer.price_per_serving or 9999),
        )
        matches = [match for match in matches if match.score >= 0.18]
        matches.sort(key=lambda match: (match.total_price, match.offer.price_per_serving or 9999, -match.score))
        best = matches[0] if matches else None
        if best:
            split_total += best.total_price
            matched_count += 1
        item_results.append(
            {
                **item.to_dict(),
                "best_offer": best.to_dict() if best else None,
                "offers": [match.to_dict() for match in matches[:8]],
            }
        )

    store_totals = build_store_totals(item_results, selected_stores)
    complete_store_totals = [entry for entry in store_totals if entry["missing_count"] == 0]
    cheapest_single_store = min(complete_store_totals, key=lambda entry: entry["total"], default=None)

    serving_prices = [
        item["best_offer"]["price_per_serving"]
        for item in item_results
        if item.get("best_offer") and item["best_offer"].get("price_per_serving") is not None
    ]

    return {
        "items": item_results,
        "missing": [item for item in item_results if item["best_offer"] is None],
        "split_total": round(split_total, 2),
        "matched_count": matched_count,
        "item_count": len(item_results),
        "average_price_per_serving": round(mean(serving_prices), 3) if serving_prices else None,
        "store_totals": store_totals,
        "cheapest_single_store": cheapest_single_store,
        "stores": selected_stores,
        "zip": zip_code,
    }


def match_offer(item: GroceryItem, offer: CatalogOffer) -> MatchedOffer:
    item_tokens = tokenize(item.name)
    haystack = " ".join([offer.product, offer.category, *offer.aliases])
    offer_tokens = tokenize(haystack)
    overlap = item_tokens & offer_tokens
    union = item_tokens | offer_tokens
    score = len(overlap) / len(union) if union else 0.0

    lowered_name = item.name.lower()
    lowered_aliases = [alias.lower() for alias in offer.aliases]
    if any(lowered_name == alias for alias in lowered_aliases):
        score += 0.6
    elif any(lowered_name in alias or alias in lowered_name for alias in lowered_aliases):
        score += 0.35
    if item_tokens and item_tokens <= offer_tokens:
        score += 0.25

    package_count = packages_needed(item, offer)
    return MatchedOffer(
        offer=offer,
        score=score,
        package_count=package_count,
        total_price=round(offer.price * package_count, 2),
    )


def packages_needed(item: GroceryItem, offer: CatalogOffer) -> int:
    if item.servings_requested and offer.servings > 0:
        return max(1, math.ceil(item.servings_requested / offer.servings))

    requested_base = to_base_amount(item.quantity, item.unit)
    offer_base = to_base_amount(offer.size_qty, offer.size_unit)
    if requested_base and offer_base and requested_base[1] == offer_base[1] and offer_base[0] > 0:
        return max(1, math.ceil(requested_base[0] / offer_base[0]))

    if item.unit in COUNT_UNITS and offer.size_unit in COUNT_UNITS and offer.size_qty > 0:
        if item.unit == "item":
            return max(1, math.ceil(item.quantity))
        return max(1, math.ceil(item.quantity / offer.size_qty))

    return max(1, math.ceil(item.quantity))


def to_base_amount(quantity: float, unit: str) -> tuple[float, str] | None:
    unit = normalize_unit(unit)
    if unit in WEIGHT_TO_OZ:
        return quantity * WEIGHT_TO_OZ[unit], "weight_oz"
    if unit in VOLUME_TO_FL_OZ:
        return quantity * VOLUME_TO_FL_OZ[unit], "volume_fl_oz"
    if unit == "dozen":
        return quantity * 12, "count"
    if unit == "ct":
        return quantity, "count"
    return None


def build_store_totals(item_results: list[dict], stores: list[str]) -> list[dict]:
    totals = []
    for store in stores:
        total = 0.0
        store_items = []
        missing = []
        for item in item_results:
            offers = [offer for offer in item["offers"] if offer["store"] == store]
            if not offers:
                missing.append(item["name"])
                continue
            best = min(offers, key=lambda offer: (offer["total_price"], offer.get("price_per_serving") or 9999))
            total += best["total_price"]
            store_items.append({"item": item["name"], **best})
        totals.append(
            {
                "store": store,
                "total": round(total, 2),
                "items": store_items,
                "matched_count": len(store_items),
                "missing_count": len(missing),
                "missing": missing,
            }
        )
    return sorted(totals, key=lambda entry: (entry["missing_count"], entry["total"] if entry["total"] else 999999))


def parse_float(value: str | None, fallback: float) -> float:
    if value is None:
        return fallback
    try:
        return float(value)
    except ValueError:
        return fallback
