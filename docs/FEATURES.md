# Feature catalogue – a decision cockpit for farmers

Principle: **every feature answers a decision a farmer has to make and puts money behind it.**
Price information alone gives small, fading gains (BP-27); decisions with numbers attached
give repeat use. A feature that serves no decision below does not get built.

References: `BP-n` → [`best_practices.md`](best_practices.md); phases → [`ROADMAP.md`](ROADMAP.md).
Priority: **M** must (MVP) · **S** should (next) · **C** could (later) · **G** gated (legal opinion first).

## 0. The decisions we serve

| Decision | Who | Season | Money at stake |
|---|---|---|---|
| D1 **When and where to sell** (sell now, store, contract forward) | producer | harvest → spring | ±5–15 % of crop value |
| D2 **When and what to buy** (fertiliser, seed, crop protection, feed, energy) | producer, livestock | autumn/winter | 30–60 % of costs |
| D3 **What to plant / how many animals** | producer | pre-sowing | whole-farm margin |
| D4 **Field operations** (spray, sow, harvest, irrigate, protect from frost/heat) | producer | daily | yield & input waste |
| D5 **Am I paid fairly?** (vs region, vs stage, vs quality) | producer, trader | continuous | negotiating power |
| D6 **Who to trade with** | all roles | continuous | reach & price |
| D7 **What happens to me if X happens** (drought, ASF, gas spike, import surge) | all roles, advisors, banks | event-driven | risk |

## 1. Home: "Today for me" (M)

The single screen after login. Assembled from the user's interests, role, AOIs and county.

- **Watchlist cards** – price, change vs last week, **low/typical/high** label vs 5-year seasonal band (BP-24), trust strip (BP-37). D1, D2, D5
- **Field-risk strip per AOI** – next 7 days: frost, spray window, heat stress (THI), bee flight hours, drying days. D4
- **What changed this week** – largest moves in watchlist, new official releases, relevant news clusters (max 5 items). BP-12
- **Margin gauge** for the user's main enterprise (pig/feed, milk/feed, wheat/fertiliser, crush…). D1–D3
- **Release calendar** – next PÁIR, KSH, WASDE, Euronext expiry dates relevant to the watchlist. BP-7

## 2. Prices (M)

| Feature | Detail | Refs | Prio |
|---|---|---|---|
| Product page | Series by market stage, region, quality; raw + normalised to base spec | BP-6, BP-9 | M |
| Seasonality chart | Current marketing year vs 5-year band | BP-13 | M |
| Trust strip & method footer | Source link, evidence type, n, age, provisional flag, coverage badge | BP-1, BP-10, BP-14, BP-37 | M |
| Chain-gap view ("magyar élelmiszerforint") | Farm-gate → processor → wholesale → retail with the gap in HUF and % | BP-11 | M |
| Currency & units | HUF/t and EUR/t (MNB rate of the day), per-unit toggles (t, kg, head, l) | BP-15 | M |
| Basis tracker | HU cash − Euronext, history + seasonal band | BP-15 | S |
| Near me | Prices/buyers in the user's county and neighbours, map | BP-26 | S |
| EU comparison | HU vs neighbours (AT, SK, RO, PL) from EU Agri-food portal, normalised | BP-9 | S |
| Methodology & corrections | Per-series method page, changelog, corrections feed, "Hibát jelzek" | BP-3, BP-4 | M |

## 3. Decision tools (S → the paid core)

| Tool | Decision | How it works | Prio |
|---|---|---|---|
| **Sell-or-store calculator** | D1 | Seasonal carry (5-year avg price path from harvest) − storage cost (HUF/t/month, drying, shrink, interest) → break-even month; shows spread of past years, not a promise | S |
| **Forward/hedge helper** | D1 | Euronext curve + expected basis = implied local forward; lots = t ÷ 50; scenario table for ±20 % | C |
| **Input timing & affordability** | D2 | Fertiliser/wheat ratio vs seasonal pattern; gas → fertiliser pass-through from `price_transmission` | S |
| **Gross-margin planner** | D3 | Per crop/enterprise: yield × price − variable costs (FADN defaults, user override); rank crops at current prices + acreage-competition hint | S |
| **Cost-push explainer** | D2, D5 | "Why did feed go up?" – decomposition by driver from `price_transmission` (maize, soy, energy, EUR/HUF) | S |
| **Scenario / ripple** | D7 | "What if gas +50 %" / "drought in Békés" → affected enterprises, cost/price/margin, timing | C |
| **Am-I-paid-fairly check** | D5 | User enters own deal (private) → percentile vs crowd/official for product × quality × county × week; never published individually | G |

All tools show assumptions, allow overrides and label model priors (principle 4 in ROADMAP).
Sell/hold wording stays descriptive ("in 7 of 10 past years price was higher in March")
until legal review allows advice-like hints (BP-24, BP-25).

## 4. Weather & field operations (M)

| Feature | Detail | Prio |
|---|---|---|
| AOI management | Draw/import fields (also from MePAR/KAP parcel ID if feasible), group by farm | M |
| Map | OpenLayers + Adaguc WMS, time slider, layers per sector | M |
| Agro-indicators | Frost risk, GDD, spray window (wind, rain, temp, delta-T), THI, bee flight hours, drying days, soil moisture | M |
| Risk alerts | Threshold per AOI per indicator, default presets per sector | M |
| Season tracker | GDD and rainfall vs normal since sowing; phenology estimate | S |
| Weather → market link | "Frost across orchard counties → fruit price pressure" card from ripple | C |

## 5. Market news & bulletins (S)

- News clusters per node with 2–5 sources each, summary hu/en, link-only (BP-33 ToS).
- **Weekly bulletin** per sector and role, every sentence cited; generated, then human-reviewed at first.
- Extracted numbers enter as `evidence_type = news_quote`, never as transactions (BP-1).
- Harvest & yield tracker: JRC MARS, KSH, news-extracted yields by county.

## 6. Community intel (G – after GVH opinion)

| Feature | Detail | Refs |
|---|---|---|
| Input price reports first | Fertiliser, crop protection, seed, feed – "what did you pay" | BP-32 |
| Output price reports | Farm-gate deals by quality, county, week | BP-2 |
| Give-to-get | One report → 12 months detailed crowd data; official data always free | BP-17 |
| Verification | Optional invoice photo, verified weight, deleted after check | BP-18 |
| Aggregation | ≥ 5 reporters, ≤ 25 % dominance, median/IQR, lag, hierarchical fallback, decay | BP-8, BP-19, BP-22 |
| Quality control | Hold queue, rule flags, peer "about right?" prompts, moderator dashboard | BP-20, BP-21 |
| Accuracy page | Crowd vs PÁIR backtest per product | BP-23 |
| Offers & bids board | Notice board only: product, quality attrs, quantity, county, expiry; contact via masked messaging; no escrow | BP-28, BP-33 |

## 7. Alerts & channels (M)

- Types: price threshold cross, weekly % move, new crowd price available, weather indicator, new official release, watchlist news (BP-12).
- Channels: PWA push, email digest, Viber (research API cost), SMS for severe weather only (paid).
- Discipline: weekly digest default; push only for user thresholds & severe weather; cap 2 push/week; quiet hours; one-tap mute per product (BP-35).

## 8. Trust, privacy, outcomes (M)

- Data charter (hu, plain language), EU agri-data Code of Conduct alignment, export & delete my data (BP-31).
- Location stored at county level for community data; AOIs private by default.
- **Outcome ledger** for the user: "sold X % above county median", "input paid vs region" – the ROI proof (BP-30).
- Public accuracy and coverage pages.

## 9. Business model (to confirm)

| Tier | Who | Gets | Never |
|---|---|---|---|
| Free | Farmers | Official prices, seasonality, weather alerts for 2 AOIs, weekly digest, news | – |
| Pro (farmer) | Larger farms, advisors | Decision tools, unlimited AOIs & alerts, basis/forward, exports | Earlier data than free |
| Contributor | Anyone reporting | Detailed crowd data 12 months | – |
| B2B | Cooperatives, integrators, banks, insurers, advisors | API, regional benchmarks, scenario runs, white-label dashboards for members | Individual reports, time advantage |

Rationale: BP-29 (a paying segment early), BP-34 (low farmer willingness to pay), BP-7 (simultaneous release).

## 10. Deliberately out of scope

- Hardware, sensors, own weather stations (BP-28).
- Trading execution, escrow, inventory, input retail (BP-28).
- Competing classifieds portal (BP-33).
- Buy/sell recommendations before legal review (BP-24, BP-25).
- Full-text news republishing.
