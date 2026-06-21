# Live Pricing Plan

The app is ready for live price providers, but the first version intentionally uses `data/catalog.csv` because grocery prices are location-specific and most retailer websites do not provide simple public price APIs.

## Recommended Provider Order

1. Instacart Developer Platform
2. Amazon Creators/Product Advertising API for Amazon.com offers
3. Manual CSV import for stores without public APIs
4. Paid grocery data provider, if the budget makes sense

## Instacart

Instacart's current Developer Platform documentation says it supports shopping list integrations that map products to nearby retailers with real-time inventory and pricing, plus nearby retailer lookup by postal code.

Docs:

- https://docs.instacart.com/developer_platform_api
- https://docs.instacart.com/developer_platform_api/api/products/create_shopping_list_page

This is likely the cleanest way to cover Publix, Aldi, and Sam's Club where Instacart supports those retailers in your ZIP code.

## Amazon

Amazon and Amazon Fresh should be tracked separately. Amazon's old PA-API documentation now states PA-API deprecation and points developers toward Creators API. Price resources are available in the Product Advertising API documentation, but this path generally requires Amazon affiliate/API approval.

Amazon Fresh prices are location-sensitive. I found Amazon advertising documentation that distinguishes Fresh offers from Amazon.com core offers and mentions live pricing inside Fresh ad products, but not a broad public consumer price API for Fresh.

Docs:

- https://webservices.amazon.com/paapi5/documentation/
- https://webservices.amazon.com/paapi5/documentation/use-cases/buying-price.html
- https://advertising.amazon.com/resources/ad-specs/fresh

## Sam's Club

Sam's has advertiser-oriented APIs. The Catalog Item Search API searches items in an advertiser's catalog, not a general shopper price API for every member account.

Docs:

- https://developer.samsclub.com/API/catalog-item-search/

## Publix and Aldi

I did not find official broad public product-price APIs for Publix or Aldi. Practical options are:

- Instacart, where available.
- Export/import from receipts or manually maintained price CSV.
- A paid data provider.
- Store-specific private APIs or scraping, which can be brittle and may violate terms.

## Provider Interface to Add Next

A provider should return rows equivalent to `data/catalog.csv`:

```json
{
  "store": "Aldi",
  "product": "Whole Milk Gallon",
  "aliases": ["whole milk", "milk"],
  "size_qty": 1,
  "size_unit": "gal",
  "package_desc": "1 gallon",
  "price": 3.19,
  "servings": 16,
  "url": "https://...",
  "last_updated": "2026-06-21",
  "zip": "33511"
}
```
