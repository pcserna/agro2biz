# Agro2Biz – project context for Claude Code

## Goal
Web platform for Hungarian agriculture professionals that concentrates market
information and reduces the information asymmetry held by retailers/buyers.
Language: Hungarian first, English second. Must work well on desktop, tablet, mobile.

Three pillars:
1. **Weather** – forecasts for user-saved areas of interest (AOIs) and layers,
   served by the existing **Adaguc** WMS service (may be migrated/extended).
   Derived agro-indicators per sector (frost risk, GDD, spray windows, soil
   moisture, livestock heat stress THI, bee flight hours, drying days).
2. **Market bulletins** – aggregated from online sources with references:
   prices, qualities, quantities, yield news. Every figure links to its source.
3. **User intel** – users share offers, bids and anonymous price reports.
   Aggregated "crowd price" published only above a minimum number of reporters.

Coverage goal: as many agricultural sectors as have usable information
(arable, industrial crops, horticulture, wine, livestock, aquaculture,
beekeeping, feed & forage, byproducts & biomass, inputs; organic as a flag).

## Architecture decisions (planned)
- Azure Container Apps environment: Next.js web (PWA, /hu default, /en),
  FastAPI API, Adaguc container, ingestion jobs as Container Apps Jobs.
- PostgreSQL Flexible Server: PostGIS (AOIs), ltree (dropdown hierarchy),
  pg_trgm, pgvector (news dedup), built-in `hungarian` full-text config.
  Adaguc gets its own metadata database.
- Blob storage for raw fetched documents and NetCDF.
- Auth: Entra External ID.
- Maps: OpenLayers (native WMS + time dimension).

## Data model concepts
- Interest taxonomy is a **graph**, not a tree: `node` + typed `edge`
  (is_a, byproduct_of, input_to, substitute_for, pollinated_by...).
  Dropdowns walk `is_a`; other edges drive related content.
- Each product node has an `attrs_schema` for quality attributes
  (wheat: protein, moisture, falling number; honey: type, HMF; biomass: moisture, GJ/t).
- Prices carry a `market_stage` (farm-gate, bulk purchase, processor, wholesale,
  retail) – the gap between stages is what exposes the asymmetry.
- User interests carry a role: producer | buyer | processor | trader | advisor.
- Each node shows a data-coverage badge (official / aggregated / community only).

## Data sources (tiers)
- **A (official, structured):** AKI PÁIR (cereals, oilseeds, soy, pig, cattle,
  sheep, poultry, eggs, milk, fruit & veg incl. wholesale market, wine, tobacco),
  AKI HALár (fish), AKI FADN/tesztüzem (farm cost structures), KSH,
  EU Agri-food Data Portal APIs, JRC MARS, Euronext, WASDE.
- **B (semi-structured, LLM extraction):** association classifieds (e.g. OMME
  honey ads), forums, news portals (Agrárszektor, Agroinform, Magyar Mezőgazdaság, NAK).
- **C (community):** minor species, herbs, most biomass – user reports.
Check each source's terms of use; store summaries + links for news, not full text.

## Legal flags
- Competition law (GVH, Art. 101 TFEU): prefer aggregated, historical,
  anonymized price data; get an opinion before launching user price sharing.
- GDPR review for location and offer data.

## What exists in the repo
- `taxonomy/agribusiness_io.yaml` – physical layer: 28 agribusinesses, 75
  products/services, 10 shock types. Businesses list weighted inputs/outputs;
  edges are DERIVED (A→B via P when P ∈ A.outputs ∩ B.inputs). Includes
  service/ecosystem flows (pollination, nectar forage) with payment direction.
- `tools/ripple.py` – shock propagation over the physical layer
  (`python tools/ripple.py --list`, `python tools/ripple.py drought --lang hu`).
- `taxonomy/price_links.yaml` – price layer: external benchmarks, cost-share
  structures, sector pass-through, substitutes, co-products, competing uses,
  acreage competition, margin indicators. All coefficients `status: prior`
  (expert guesses) until estimated from data.

## Next tasks
1. Write `tools/price_transmission.py`: take price moves (e.g. maize_grain=+20%,
   natural_gas=+50%, or a benchmark) and compute via cost shares (Leontief-style,
   iterate to convergence) the break-even price change per business, apply
   pass-through, add substitute co-movement, co-product/margin effects, and
   report margin indicators. Hungarian/English output like ripple.py.
2. Add unit tests for both models (reference integrity, shares ≤ 1, convergence).
3. Add a regional dimension (county/NUTS3) so shocks can start from weather AOIs.
4. Plan estimation of priors: cost shares from FADN; pass-through, lags and
   asymmetric price transmission (farm-gate vs retail) from PÁIR time series.
5. Generate the seed interest taxonomy (hu/en labels + synonyms, CN codes,
   attrs_schema, cross-sector edges) and the Postgres schema/migrations.

## Conventions
- Python for API, ingestion and analytics. Keep models in YAML under `taxonomy/`.
- All user-facing labels need `hu` and `en`.
