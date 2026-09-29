# Agro2Biz – roadmap (v0.2 plan)

Status: planning. Nothing is built yet beyond the two YAML models and `tools/ripple.py`.
Companion documents:
- [`data_model.md`](data_model.md) – Postgres schema sketch and how the YAML models map into it
- [`price_transmission_spec.md`](price_transmission_spec.md) – design of `tools/price_transmission.py`
- [`sources.md`](sources.md) – source inventory, ingestion cadence, licence checks
- [`FEATURES.md`](FEATURES.md) – feature catalogue organised by farmer decisions, priorities, business model
- [`best_practices.md`](best_practices.md) – practices adopted from price agencies, terminals, statistics offices, crowdsourcing and agtech (BP-1…BP-37)

---

## 1. Guiding principles

1. **Legal-safe first.** Launch with official, aggregated, historical data (tier A) and
   weather. User price sharing (pillar 3) waits for the competition-law opinion.
2. **Every number has a source.** No figure reaches the UI without a `source_id`,
   fetch timestamp and link. This is the product's credibility.
3. **One vocabulary.** The interest taxonomy, the physical I/O model and the price
   model use the same product keys. The YAML ids in `taxonomy/` are the canonical keys.
4. **Models explain, they don't forecast.** Ripple and price transmission show
   mechanisms and directions with stated priors; they are labelled as such.
5. **Hungarian first.** Every user-facing string has `hu` and `en`; HU is the default route.
6. **Decisions, not dashboards.** Every feature serves one of the decisions D1–D7 in `FEATURES.md`.
7. **Price-agency discipline.** Evidence hierarchy, fixed windows, published methodology,
   versioned corrections, simultaneous release (BP-1…BP-8).
8. **Asset-light.** No hardware, inventory or trade execution (BP-28).

## 2. Phases

Durations are relative sizes for a 1–2 person team, not commitments.

### Phase 0 – Foundations (S)
Goal: a repo others can contribute to and a model layer that is tested.

| # | Deliverable | Exit criterion |
|---|---|---|
| 0.1 | Monorepo layout (see §4), `pyproject.toml`, ruff, pytest, GitHub Actions CI | CI green on every push |
| 0.2 | `tools/model_check.py` + tests: reference integrity across both YAMLs, cost shares ≤ 1, co-product yields reference real outputs, hu/en present | Fails CI on a broken reference |
| 0.3 | `tools/price_transmission.py` per spec | Converges on all scenarios, CLI output in hu/en |
| 0.4 | Fix known model issues (§6) | Regression tests for each |
| 0.5 | Request legal opinions (GVH / competition, GDPR DPIA scoping) | Lawyer engaged – long lead time, so start now |

### Phase 1 – Data backbone (M)
Goal: official prices land in Postgres with provenance, on a schedule.

| # | Deliverable | Exit criterion |
|---|---|---|
| 1.1 | Postgres schema v1 + Alembic migrations (`data_model.md`) | `alembic upgrade head` on empty DB |
| 1.2 | Seed taxonomy generator: YAML → `node`/`edge`/labels/synonyms/CN codes | Covers every product id in both YAML models |
| 1.3 | Ingestion framework: adapter interface, raw → Blob, parse → `observation`, unit/currency normalisation, run log | One adapter end-to-end, idempotent re-runs |
| 1.4 | Tier A adapters, in order: AKI PÁIR (cereals/oilseeds, pig, milk, fruit & veg wholesale), EU Agri-food Data Portal, Euronext settlement, EUR/HUF (MNB), TTF/Brent | Weekly series back-filled ≥ 5 years |
| 1.5 | Data-coverage badge computed per node | Every node shows official / aggregated / community / none |
| 1.6 | Bitemporal observations, `evidence_type`, reference window & delivery basis per series | Corrections create versions; as-of queries work (BP-1, BP-2, BP-5) |
| 1.7 | Methodology pages + release calendar data | One method page per ingested series (BP-3, BP-7, BP-10) |

### Phase 2 – MVP web app (M–L) → **first public beta**
Goal: a farmer can pick interests and an area and get weather + prices in Hungarian.

| # | Deliverable | Exit criterion |
|---|---|---|
| 2.1 | FastAPI: `/nodes` (tree via `is_a`, related via other edges), `/series`, `/aoi`, `/bulletin` | OpenAPI documented, contract tests |
| 2.2 | Next.js PWA `/hu` `/en`: onboarding (role + interests), dashboard, product page, map | Lighthouse mobile ≥ 90, works offline for last-seen data |
| 2.3 | Auth: Entra External ID (email + Google/Facebook) | Sign-up works on mobile |
| 2.4 | Weather: Adaguc behind the API, AOI drawing on OpenLayers, time slider | User saves AOI, sees forecast layers |
| 2.5 | Agro-indicators v1 per AOI: frost risk, GDD, spray window, THI, bee flight hours | Nightly job, shown on dashboard with sector filter |
| 2.6 | Market-stage view: farm-gate vs processor vs retail on one chart where data exist | Visible for at least milk, pork, wheat→flour, eggs |
| 2.7 | "What moves this price" panel from price_links.yaml (benchmarks, cost shares, substitutes) | Labelled "model prior" |
| 2.8 | Home "Today for me": watchlist cards with low/typical/high vs seasonal band, AOI risk strip, what-changed, margin gauge | New user sees value in first session without contributing (BP-36) |
| 2.9 | Alerts: price threshold, weekly move, weather indicator; weekly digest; push cap | Opt-out rate tracked (BP-12, BP-35) |
| 2.10 | Trust strip + "Hibát jelzek" + corrections feed | Every figure shows source, age, evidence type (BP-4, BP-37) |
| 2.11 | Data charter (hu), privacy settings, export/delete | Legal review done (BP-31) |

MVP scope decision: **arable + livestock + honey** first (best official coverage plus a
clear community gap for honey); other sectors show whatever tier A data exist.

### Phase 2b – Decision tools (M) → **first paid tier**
| # | Deliverable | Exit criterion |
|---|---|---|
| 2b.1 | Sell-or-store calculator (seasonal carry vs storage cost) | Backtested on 5 years of PÁIR wheat/maize |
| 2b.2 | Gross-margin planner with FADN defaults | Top 8 arable crops + pig, dairy, broiler, honey |
| 2b.3 | Cost-push explainer from `price_transmission` | Decomposition sums to total move |
| 2b.4 | Basis tracker and near-me prices | Wheat, maize, sunflower, rapeseed |
| 2b.5 | Input timing (fertiliser affordability vs seasonal pattern) | – |
| 2b.6 | Billing (Pro), B2B pilot with one cooperative or integrator | Signed pilot (BP-29) |

### Phase 3 – News & bulletins (M)
| # | Deliverable | Exit criterion |
|---|---|---|
| 3.1 | Tier B crawlers (Agrárszektor, Agroinform, Magyar Mezőgazdaság, NAK) – headline, summary, link only | ToS checked per source (`sources.md`) |
| 3.2 | LLM extraction: entities → taxonomy nodes, prices/quantities → candidate observations with confidence | Precision ≥ 90 % on a hand-labelled set of 200 items |
| 3.3 | Dedup with pgvector + `hungarian` FTS | Same story from 3 portals shows once with 3 links |
| 3.4 | Weekly generated bulletin per node / role (hu first) | Every sentence cites a source |
| 3.5 | Review queue for low-confidence extractions | Admin UI |

### Phase 4 – User intel (M) — gated on legal opinion
| # | Deliverable | Exit criterion |
|---|---|---|
| 4.0 | Input price reports first (fertiliser, crop protection, seed, feed), give-to-get, optional invoice verification | ≥ 5 reporters per published cell (BP-17, BP-18, BP-32) |
| 4.1 | Offers / bids board (quality attrs from `attrs_schema`, county-level location only) | GDPR DPIA signed off |
| 4.2 | Anonymous price reports; crowd price published only at k ≥ N reporters (N from the legal opinion, default 5), lagged, banded | Unit tests on the k-threshold view |
| 4.3 | Abuse controls: hold queue, rule flags, peer confirmation, reputation, moderator dashboard | Documented (BP-20, BP-21) |
| 4.4 | Aggregation engine: median/IQR, dominance/p% rule, secondary suppression, hierarchical fallback, decay | Property tests; no cell below threshold ever published (BP-8, BP-19, BP-22) |
| 4.5 | Accuracy page: crowd vs PÁIR backtest | Published per product (BP-23) |
| 4.6 | "Am I paid fairly?" private percentile check | Never exposes individual reports |

### Phase 5 – Scenario & regional analytics (M)
| # | Deliverable | Exit criterion |
|---|---|---|
| 5.1 | Regional dimension: NUTS3 (20 units) weights per agribusiness from KSH ÁMÖ 2020 / FADN | Shock can start from a county |
| 5.2 | Weather → shock bridge: AOI indicators trigger `drought`, `late_frost`, `heatwave` scenarios with regional scaling | Automatic "possible ripple" card |
| 5.3 | Estimated coefficients replace priors (§5) | Each coefficient has `status: estimated`, source, date, interval |
| 5.4 | Scenario UI: "what if gas +50 %" in the browser, using the same Python engine via API | Same numbers as CLI |
| 5.5 | B2B API and member dashboards for cooperatives/integrators | Same data, same release time as public (BP-7) |

## 3. Architecture (confirmed from CLAUDE.md, with additions)

```
            ┌──────────── Azure Container Apps env ─────────────┐
 browser ─► │ web (Next.js PWA) ─► api (FastAPI) ─► Postgres    │
            │                       │   │           (PostGIS,    │
            │                       │   └► adaguc ─► adaguc-db   │
            │ jobs: ingest-*, indicators, bulletin, llm-extract │
            └───────────────────────┬───────────────────────────┘
                                    └► Blob: raw/, netcdf/, exports/
```

Additions:
- **IaC:** Bicep (Azure-native, no state file) in `infra/`. One environment per stage (dev, prod).
- **Secrets:** Key Vault + managed identity; no secrets in env files.
- **Observability:** Application Insights; every ingestion run writes a `job_run` row.
- **Models as a library:** `packages/agromodels` (ripple, transmission, loaders) imported by
  the API and jobs; `tools/*.py` become thin CLIs over it.
- **LLM calls** only from jobs, never from request paths; cache by document hash.

## 4. Repository layout (target)

```
apps/web/            Next.js PWA
apps/api/            FastAPI
jobs/ingest/         one module per source adapter
jobs/indicators/     agro-indicators per AOI
packages/agromodels/ ripple, price transmission, YAML loaders, validation
db/migrations/       Alembic
taxonomy/            YAML models (source of truth for keys)
tools/               CLIs
infra/               Bicep
docs/
tests/
```

## 5. Estimating the priors (Phase 5.3, groundwork from Phase 1)

| Coefficient | Data | Method |
|---|---|---|
| Cost shares | AKI FADN (tesztüzemi rendszer) by farm type | Direct shares, 3-year average; map FADN cost lines to product keys |
| Benchmark elasticities & lags | PÁIR weekly vs Euronext / EU prices × EUR/HUF | Log-diff regression, distributed lags; cointegration + ECM where series are I(1) |
| Pass-through by stage | PÁIR farm-gate vs processor vs retail (KSH CPI) | Asymmetric (threshold) ECM: separate up/down adjustment speeds |
| Substitute co-movement | PÁIR feed grains, protein meals | Correlation of log returns; rolling window |
| Acreage response | KSH sowing areas vs relative prices at sowing | Nerlove-type model, pooled across crops |

Rule: an estimate replaces a prior only if its interval excludes nonsense (sign, > 1)
and it is stored with `source`, `period`, `method`, `ci`. Otherwise shrink toward the prior.

## 6. Known issues in the current models

1. **Drought shows "maize_grain cheaper".** In `ripple.py`, capacity loss at a
   consumer (feed mill) emits a demand-down signal on an input that is itself scarce,
   so the report mixes "scarcer" and "cheaper" for the same product. Fix: suppress the
   demand signal for inputs already under a supply shock in the same scenario, or net
   supply and demand per product before pricing.
2. **`eur_huf` drives `"*tradable"`** but no product carries a `tradable` flag.
   Add `tradable: true` to products in `agribusiness_io.yaml` and resolve the wildcard in the loader.
3. **Labour, land and capital** are only partly represented (labour is a product, land
   is not). Fine for v0.1; document that cost-share remainders are "unmodelled".
4. **`dairy_herd` co-product** has no `input`; the transmission engine must handle
   joint-production processes without a single driving input.

## 7. Risks

| Risk | Mitigation |
|---|---|
| Competition-law exposure from price sharing | Phase 4 gated; k-anonymity, lag, banding; legal opinion before launch |
| Source ToS forbid scraping / redistribution | Per-source licence register; summaries + links only; ask AKI for data agreement |
| Sparse data for minor sectors | Coverage badges set expectations; community tier fills gaps later |
| LLM extraction errors presented as fact | Confidence threshold, review queue, "extracted" label, always link source |
| Adaguc operational load | Pre-render common layers; cache tiles at the API; consider moving to managed storage later |
| Cold start (no users → no crowd data) | MVP is valuable without users: official prices + weather + models |
| No paying segment (the Gro Intelligence failure) | B2B pilot in Phase 2b; costs sized for the Hungarian market (BP-29) |
| Farmers don't see ROI | Outcome ledger and decision tools, not raw prices only (BP-27, BP-30) |
| Distrust of data use | Data charter, no resale of individual data, delete button (BP-31) |

## 8. Open decisions (need the owner)

1. MVP sector focus – proposed arable + livestock + honey. Confirm or change.
2. Weather model inputs for Adaguc – HungaroMet products (licence?), ECMWF open data, DWD ICON-EU (open). Which are available today?
3. Monetisation – proposed in `FEATURES.md` §9: free + Pro + contributor unlock + B2B. Confirm, and name a first B2B pilot partner.
4. Team and hosting budget – determines whether Phase 2 and 3 run in parallel.
5. Is there an existing Adaguc deployment and dataset to reuse, and where does it run?
6. Research: CMO Regulation Art. 209–210a (agricultural competition carve-outs) – could widen what producer organisations may share.
7. Partnerships: AKI (data agreement), Agroinform (asking-price layer instead of competing), NAK (distribution to members).
