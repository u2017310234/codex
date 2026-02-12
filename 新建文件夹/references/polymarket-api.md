# Polymarket API Notes (for this skill)

This skill is designed around the public markets endpoint:

- `https://gamma-api.polymarket.com/markets`

The script currently tries a paginated request first:

- Query params used: `limit`, `offset`, `active`, `closed`, `archived`

Then it falls back to a plain endpoint request when pagination is unavailable.

## Response shape support

The script accepts multiple payload shapes:

1. Root JSON array of market objects.
2. Root object containing one of these arrays:
   - `markets`
   - `data`
   - `items`
   - `results`
3. Nested object forms like:
   - `{ "data": { "markets": [...] } }`

## Market fields consumed

The script reads a subset of common fields:

- Identity/url: `id`, `conditionId`, `slug`, `url`, `marketUrl`
- Text: `question`, `title`, `name`
- Status: `active`, `closed`, `archived`, `acceptingOrders`
- Dates: `endDate`, `end_date`, `endTime`, `endDatetime`, `resolveDate`
- Prices: `yesPrice`, `noPrice`, `outcomes`, `outcomePrices`
- Volume/sort: `volume24hr`, `volume24h`, `volume24Hours`, `oneDayVolume`, `volume`, `totalVolume`
- Tags/category: `tags`, `category`, `subcategory`, `groupItemTitle`, `marketType`

## Translation

Optional title translation supports DeepL only:

- Default endpoint: `https://api-free.deepl.com/v2/translate`
- API key env: `POLYMARKET_TRANSLATE_API_KEY`
- Endpoint override env: `POLYMARKET_TRANSLATE_ENDPOINT`

If translation fails, the script keeps original output and records a warning.
