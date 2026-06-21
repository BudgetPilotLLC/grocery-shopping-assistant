# Amazon and Amazon Fresh Prices

The assistant treats `Amazon` and `Amazon Fresh` as separate stores.

- `Amazon` is for regular Amazon.com grocery, pantry, bulk, and household listings.
- `Amazon Fresh` is for location-sensitive grocery delivery or Amazon Fresh store offers.

Both are currently represented in `data/catalog.csv`, so the comparison UI includes them immediately.

## Live Price Reality

Amazon's older Product Advertising API documentation says PA-API is deprecated as of May 15, 2026 and points developers to the Creators API. That is the likely path for regular Amazon.com product offers if the account has API access.

Amazon's Selling Partner Product Pricing API can retrieve pricing and offer information for products in the Amazon catalog, but it is built for sellers and requires seller/API roles.

Amazon Fresh is more complicated because Fresh offers are local and delivery-specific. Amazon's own advertising docs distinguish Fresh offers from Amazon.com core offers, and mention Fresh REC ads can include live pricing, but that is an advertising product rather than a general consumer grocery price API.

Practical options:

- Keep Amazon and Amazon Fresh rows updated in `data/catalog.csv`.
- Add a credentialed Amazon/Creators API connector for regular Amazon.com offers.
- Use a paid grocery data provider if exact Fresh prices are required by ZIP code.
- Avoid scraping unless you explicitly accept the fragility and terms-of-service risk.

## Credentials

Do not put your normal Amazon shopping email/password in `.env`.

Use `.env` for official API/provider credentials only:

```text
AMAZON_PROVIDER=disabled
AMAZON_MARKETPLACE=US
AMAZON_ASSOCIATE_TAG=
AMAZON_ACCESS_KEY_ID=
AMAZON_SECRET_ACCESS_KEY=
AMAZON_CREATORS_API_TOKEN=
AMAZON_FRESH_PROVIDER=disabled
AMAZON_FRESH_ZIP=
```

Logged-in website scraping is not the default plan because it is fragile, may violate site terms, can break on MFA/CAPTCHA, and would place sensitive shopping-account access inside a headless browser/container.

If we later decide to do an explicit personal-use assisted capture flow, keep it separate from normal API credentials. A safer pattern would be:

- You open Amazon/Fresh yourself.
- The app imports a cart/export/page snapshot you provide.
- The assistant extracts prices from that snapshot without storing your Amazon password.

Sources:

- https://webservices.amazon.com/paapi5/documentation/
- https://developer-docs.amazon.com/sp-api/docs/product-pricing-api
- https://advertising.amazon.com/resources/ad-specs/fresh
