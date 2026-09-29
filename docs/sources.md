# Source register

Every source needs a licence check before an adapter is merged. `licence` values:
`open` (explicit open licence), `attribution` (reuse allowed with citation),
`link-only` (store title/summary/link, no content), `agreement` (need written permission), `unknown`.
All entries below start as `unknown` until checked.

| Tier | Source | Content | Access | Cadence | Priority | Licence |
|---|---|---|---|---|---|---|
| A | AKI PÁIR | Cereals, oilseeds, soy, pig, cattle, sheep, poultry, eggs, milk, F&V incl. Budapest wholesale market, wine, tobacco | Web tables / downloadable reports | Weekly | P1 | unknown – ask AKI for a data agreement |
| A | AKI HALár | Fish prices | Web | Monthly | P3 | unknown |
| A | AKI FADN (tesztüzemi rendszer) | Farm cost structures by type | Annual reports / tables | Yearly | P2 (for estimation) | unknown |
| A | KSH (STADAT) | Production, sowing areas, livestock numbers, producer price indices, CPI | API / CSV | Monthly/yearly | P1 | open (verify) |
| A | EU Agri-food Data Portal | EU prices by member state (cereals, meat, dairy, F&V) | REST API | Weekly | P1 | open (verify) |
| A | MNB | EUR/HUF official rate | Web service | Daily | P1 | open (verify) |
| A | Euronext | Wheat, maize, rapeseed settlement | Web / delayed data | Daily | P2 | verify redistribution terms |
| A | JRC MARS bulletins | EU crop yield forecasts | PDF/web | Monthly | P3 | attribution (verify) |
| A | USDA WASDE | World supply/demand | API/CSV | Monthly | P3 | open (US public domain) |
| A | TTF gas, Brent | Energy benchmarks | Source TBD (licence-dependent) | Daily | P2 | verify |
| B | OMME classifieds | Honey offers and prices | Web | Daily | P2 | ask the association |
| B | Agrárszektor, Agroinform, Magyar Mezőgazdaság, NAK | News | RSS/web | Daily | P2 | link-only |
| C | Users | Offers, bids, price reports | App | Continuous | Phase 4 | own ToS |
| W | Weather: ECMWF open data, DWD ICON-EU, HungaroMet | Forecast fields for Adaguc | GRIB/NetCDF | 2–4×/day | P1 | per provider |

## Adapter contract

```python
class Adapter(Protocol):
    source_id: str
    def discover(self, since: date) -> Iterable[RawRef]: ...   # what is new
    def fetch(self, ref: RawRef) -> RawDoc: ...                 # bytes -> Blob raw/<source>/<date>/<hash>
    def parse(self, doc: RawDoc) -> Iterable[ObservationIn]: ... # pure, unit-tested on saved fixtures
```

- Re-runs are idempotent (upsert on `(series_id, period_start)`; skip documents by hash).
- Each adapter ships fixture files and a parser test; layout changes on source sites fail loudly.
- Politeness: identify the crawler in User-Agent, respect robots.txt, ≤ 1 request/s.
