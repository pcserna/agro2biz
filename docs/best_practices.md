# Best practices adopted from other industries

Research of 2026-09-29 (web). Items marked *(secondary)* were checked against search
extracts, not the full primary document; *(design)* marks our own proposal without a direct precedent.
Each practice ends with the concrete rule it becomes in Agro2Biz (→ **BP-n**, referenced from `FEATURES.md`).

## 1. Price reporting agencies and statistical offices – *how to make a number trustworthy*

| # | Practice | Precedent | Agro2Biz rule |
|---|---|---|---|
| BP-1 | **Data hierarchy**: transactions > firm bids/offers inside the traded range > indications | IOSCO PRA Principles; Fastmarkets methodology *(secondary)* – https://www.iosco.org/library/pubdocs/pdf/IOSCOPD391.pdf | Every observation has `evidence_type` (`transaction, firm_bid, firm_offer, indication, asking_price, news_quote, community_report`); aggregation weights by it; badge shown next to each figure |
| BP-2 | **Fixed assessment window & basis** | Argus cut-off times and delivery windows *(secondary)* | Each series has a fixed reference period (ISO week, cut-off Fri 12:00 CET) and delivery basis (farm-gate / delivered / FCA); late reports roll into the next period |
| BP-3 | **Published, versioned methodology with change consultation** | S&P Platts annual review + subscriber notes – https://www.spglobal.com/platts/en/our-methodology/methodology-review-change | `/hu/modszertan` page per series; changelog with effective dates; 2–4 weeks comment period for material changes |
| BP-4 | **Corrections as new versions, complaints route, 5-year records** | IOSCO PRA Principles (records, complaints, external assurance) *(secondary)* – https://www.iosco.org/library/pubdocs/pdf/IOSCOPD506.pdf | "Hibát jelzek" button on every figure → ticket; public corrections feed; raw inputs kept ≥ 5 years in Blob |
| BP-5 | **Vintages (bitemporal data)** | ALFRED `realtime_start/end` – https://alfred.stlouisfed.org/help | `observation` gets `valid_from/valid_to` + `revision_reason`; estimation uses as-known-then data (no look-ahead bias) |
| BP-6 | **SDMX-style series keys & codelists** | Eurostat / KSH SDMX APIs | Series key = `product × market_stage × region × evidence_type × unit × freq`; CN and NUTS codelists |
| BP-7 | **Release calendar, simultaneous release, revision policy** | IMF SDDS – https://dsbb.imf.org/sdds/overview | Public calendar of own + upstream releases (PÁIR, KSH, WASDE); **no early access for paying tiers** (depth and API may be paid, time advantage never) |
| BP-8 | **Confidentiality: minimum count, dominance, p% rule, secondary suppression** | ABS confidentiality guide; SDC handbook – https://sdctools.github.io/HandbookSDC/ | Crowd cell published only with ≥ 5 distinct reporters, no reporter > 25 % of volume (or p% rule), secondary suppression across region/product totals; publish median + IQR, never single values |
| BP-9 | **Normalise to a reference quality/stage before comparing** | ISN EU pig price comparison (79 % dressing, 57 % lean) – https://www.schweine.net/markt/schweinepreisvergleich.html | `attrs_schema` defines a base spec per product (e.g. wheat 12.5 % protein); show raw and normalised price |
| BP-10 | **Method in the chart footer** | AHDB Corn Returns (who reports, window, publish day) – https://ahdb.org.uk/cereals-oilseeds/ex-farm-prices-summary | Every chart footer: source, reporters/coverage, reference window, publish day, last update |
| BP-11 | **Margin along the chain as a public good** | FranceAgriMer price & margin observatory – https://observatoire-prixmarges.franceagrimer.fr/ | "Hungarian food forint" view: farm-gate → processor → wholesale → retail, official data only, no single-firm accusations |

## 2. Market terminals – *how to make a number useful*

| # | Practice | Precedent | Agro2Biz rule |
|---|---|---|---|
| BP-12 | **Watchlist alerts** (crossing, % change, applied to every item) | TradingView watchlist alerts – https://www.tradingview.com/support/solutions/43000739708-watchlist-alerts/ | User interests = watchlist; alert types: threshold cross, weekly % move, crowd price newly available, weather indicator trigger per AOI |
| BP-13 | **Seasonality overlay** | Bloomberg SEAG; LSEG example – https://developers.lseg.com/en/article-catalog/article/commodity-seasonality-charts-ldlib | Default chart: current marketing year vs 5-year min/max band and mean (cereals Jul–Jun) |
| BP-14 | **Provisional flag + uncertainty band** | Vortexa provisional data | Current period labelled "előzetes"; show n and IQR, not a lone point |
| BP-15 | **Basis & forward view** | Kansas State basis guide – https://www.agmanager.info/sites/default/files/MF1003_Basis.pdf; Barchart local basis – https://www.barchart.com/solutions/data/grbids | Basis = HU cash − Euronext (in EUR/t via MNB rate), history with seasonal band; implied local forward = futures curve + expected basis |
| BP-16 | **Processing spreads** | CME crush spread; EIA spark spread | Metric crush margin (sunflower, rapeseed), biogas/biomass spark-type spread, fertiliser (urea − gas × gas per t) – extends `margins` in price_links.yaml |

## 3. Crowdsourcing platforms – *how to get honest data in*

| # | Practice | Precedent | Agro2Biz rule |
|---|---|---|---|
| BP-17 | **Give-to-get** | Glassdoor (1 contribution = 12 months access) – https://help.glassdoor.com/s/article/Give-to-get-policy?language=en_US; FBN (≥ 3 input prices) – https://www.fbn.com/community/faq/what-is-price-transparency | One price report unlocks detailed crowd data for 12 months; official data always free; advisors/new users get a non-reporting path |
| BP-18 | **Verification tiers** | Levels.fyi verified (document proof) – https://levels.fyi/verified | Optional invoice/delivery note photo, used for verification then deleted; verified reports weigh more; "verified share" on aggregates |
| BP-19 | **Freshness & decay** | GasBuddy age display; Numbeo 12-month window – https://www.numbeo.com/common/motivation_and_methodology.jsp | Age shown on every figure; per-product half-life for report weights (short for fresh produce, long for hay) |
| BP-20 | **Peer confirmation** | Waze crowd verification | "Is this price about right? yes / no / changed" prompts to peers in same product × county; offers auto-expire unless reconfirmed |
| BP-21 | **Hold queue for new contributors + rule flags** | Wikipedia pending changes; OSMCha | First N reports of a new account don't count until reviewed; flags: outside robust range, bursts, same device/IP, new account; labelled flags stored for a later ML model |
| BP-22 | **Robust aggregation + hierarchical fallback** | LinkedIn Salary (cohort thresholds, outlier removal, Bayesian smoothing) – https://arxiv.org/pdf/1705.06976 | Median/MAD trimming; thin county cells blended toward NUTS2/national; optional small noise + rounding against differencing attacks |
| BP-23 | **Publish your own accuracy** | Zillow Zestimate error by region *(secondary)* | Backtest crowd prices against PÁIR; publish median error per product; show n, spread, verified share on each crowd figure |
| BP-24 | **Low/typical/high label; advice only when confident** | Google Flights price insights – https://support.google.com/travel/answer/6235879 | Each price labelled vs its seasonal band; any sell/hold hint only above a confidence threshold, with stated hit rate – **after legal review** |

## 4. Competition law – *what the precedents say*

- **EU Horizontal Guidelines 2023, ch. 6** – no safe harbour; aggregated and historical data less likely sensitive; data pools should be run by an independent party, participants see own data + aggregate; genuinely public data (equally available to all, incl. buyers) treated more leniently. https://competition-policy.ec.europa.eu/system/files/2023-07/2023_revised_horizontal_guidelines_en.pdf
- **US DOJ withdrew its safety zone (2023)** – old rule (third-party manager, data > 3 months old, ≥ 5 providers, none > 25 %) called "formalistic"; poultry cases cited. https://www.arnoldporter.com/en/perspectives/advisories/2023/02/no-safe-harbors-doj-signals-increased-scrutiny
- → **BP-25**: Agro2Biz acts as independent aggregator; crowd prices published to everyone (farmers *and* buyers), lagged, aggregated; no current/future intentions; offers/bids remain bilateral notices. k ≥ 5 / 25 % / lag is a technical minimum, not a legal clearance – the GVH opinion is still required. Open research item: CMO Regulation Art. 209–210a agricultural carve-outs.

## 5. Agtech market – *what worked, what failed*

| # | Lesson | Evidence | Agro2Biz rule |
|---|---|---|---|
| BP-26 | Local prices beat national averages | Barchart: 4,000+ buyers, "5 nearest elevators" by zip | Show buyers/prices near the user's AOI (county), not only national PÁIR |
| BP-27 | Price information alone yields small, fading gains | Esoko RCT Ghana: +7 % yam price year 1 only; e-NAM ~5.5 % with trust issues | Pair every price with a decision tool (sell-now vs store, where to sell, input timing) |
| BP-28 | Don't build hardware, inventory or trade execution | Farmers Edge (−99 % from IPO); FBN input-retail cutbacks; Tridge losses | Asset-light: public data, satellites, Adaguc; offers board stays a notice board – no escrow, no stock |
| BP-29 | A broad "AI insights" product without a paying buyer fails | Gro Intelligence closed 2024 (~$120M raised) – https://techcabal.com/2024/06/02/kenya-data-analytics-gro-intelligence-shuts-down/ | Choose one paying B2B segment early (cooperatives/integrators/banks/insurers); farmers on freemium; keep costs small-market sized |
| BP-30 | Free information still needs visible ROI | UK growers voted out AHDB horticulture/potato levy (2021) | Show outcome metrics to users ("sold 4 % above county median", "saved X HUF on fertiliser") |
| BP-31 | Data trust is the top barrier | AFBF: 77 % worry who accesses data – https://texasfarmbureau.org/farm-bureau-survey-farmers-want-control-data/ | Plain-Hungarian data charter; align with EU Code of Conduct on agricultural data sharing; no resale of individual data; one-click delete |
| BP-32 | Start crowd prices with **inputs** | FBN price transparency on inputs | First crowd category: fertiliser, crop protection, seed, feed prices paid |
| BP-33 | Don't fight incumbent classifieds | Agroinform Piactér: 130k+ ads | Partner or ingest asking prices (if ToS allow) as a separate `asking_price` layer |
| BP-34 | Weather risk is Europe's top concern; low willingness to pay | McKinsey Global Farmer Insights 2024 | Lead acquisition with free AOI weather-risk alerts; price depth, tools and API are the paid layers |

## 6. Engagement

- **BP-35 Notification discipline** – opt-outs driven by frequency (25 %) and irrelevance (30 %) (Braze). Default: weekly digest on a sector-appropriate day; push only for user-defined thresholds and severe weather; cap ~2 push/week; per-channel settings; bundle per AOI/product. Older users opt out more *(vendor claim, unverified)* → email/Viber stay first-class channels.
- **BP-36 Value in the first session** *(design)* – onboarding picks products, role, county and shows official price, stage gap and one AOI weather indicator before any contribution is asked.
- **BP-37 Trust strip on every figure** – source or "community", n, age, verified share, coverage badge, published error (combines BP-10, 14, 18, 19, 23).
