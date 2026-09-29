# Data model v1 (Postgres sketch)

Target: PostgreSQL Flexible Server with `postgis`, `ltree`, `pg_trgm`, `vector`.
Migrations with Alembic in `db/migrations/`. This is a sketch; column types will be refined.

## 1. Taxonomy (interest graph)

```sql
node (
  id           text primary key,          -- same keys as taxonomy/*.yaml (e.g. 'maize_grain')
  kind         text not null,             -- sector | group | product | service | ecosystem | input
  path         ltree,                     -- primary is_a path, for fast dropdowns
  labels       jsonb not null,            -- {"hu": "...", "en": "..."}
  synonyms     jsonb default '{}',        -- {"hu": ["tengeri", "csöves kukorica"], "en": [...]}
  cn_codes     text[],                    -- EU Combined Nomenclature
  unit         text,                      -- canonical unit for prices (t, kg, head, l, hl...)
  attrs_schema jsonb,                     -- JSON Schema for quality attributes
  organic_ok   boolean default true,
  coverage     text                       -- official | aggregated | community | none (computed)
)
edge (
  src text references node, dst text references node,
  type text not null,                     -- is_a | byproduct_of | input_to | substitute_for | pollinated_by | co_product_of
  weight real, source text,               -- 'agribusiness_io' | 'price_links' | 'manual'
  primary key (src, dst, type)
)
```

`input_to`, `byproduct_of`, `substitute_for`, `co_product_of` edges are **generated**
from the two YAML models by the seed script; `is_a` and `pollinated_by` are curated
in a new `taxonomy/interests.yaml`. Businesses from `agribusiness_io.yaml` are
stored in `agribusiness` (not `node`) and linked to users' roles.

## 2. Sources and observations

```sql
source (id text pk, name jsonb, tier char(1), url text, licence text, licence_checked date, terms_url text)
document (id uuid pk, source_id, url, fetched_at, content_hash, blob_path, lang)
series (
  id bigserial pk, node_id, source_id,
  market_stage text,          -- farm_gate | bulk_purchase | processor | wholesale | retail | export | benchmark
  unit text, currency text,   -- canonical after normalisation
  region text,                -- 'HU' or NUTS3 code
  quality jsonb,              -- validated against node.attrs_schema
  organic boolean default false,
  frequency text,             -- weekly | monthly | daily
  delivery_basis text,        -- farm_gate | delivered | fca | ... (BP-2)
  window_rule text,           -- e.g. 'iso_week, cutoff Fri 12:00 Europe/Budapest'
  base_spec jsonb,            -- reference quality for normalisation (BP-9)
  methodology_id int          -- -> methodology (BP-3)
)
-- series key follows SDMX-style dimensions (BP-6):
-- product × market_stage × region × evidence_type × unit × frequency
observation (
  series_id, period_start date, period_end date,
  value numeric, value_normalised numeric, value_low numeric, value_high numeric, volume numeric,
  evidence_type text,          -- transaction | firm_bid | firm_offer | indication | asking_price | news_quote | community_report (BP-1)
  n_reporters int,             -- for aggregates
  provisional boolean,         -- current period (BP-14)
  document_id, extracted_by text,  -- 'adapter' | 'llm:<version>' | 'aggregator:<version>'
  confidence real,
  valid_from timestamptz not null default now(),   -- bitemporal vintages (BP-5)
  valid_to   timestamptz,                          -- null = current version
  revision_reason text,
  primary key (series_id, period_start, valid_from)
)
-- as-of view: where valid_from <= :asof and (valid_to is null or valid_to > :asof)

methodology (id serial pk, series_scope text, version text, effective_from date,
             body_hu text, body_en text, change_note text)             -- BP-3
correction (id serial pk, series_id, period_start, old_value, new_value, reason, published_at)  -- BP-4
complaint (id uuid pk, user_id null, series_id, period_start, text, status, resolution, created_at, closed_at)
release (id serial pk, source_id, series_scope, scheduled_at timestamptz, released_at timestamptz)  -- BP-7
```

Normalisation rule: raw value + raw unit + raw currency are kept in `document`/blob;
`observation` holds canonical unit (HUF per node.unit) plus EUR via MNB daily rate.

## 3. News

```sql
news_item (id uuid pk, source_id, url unique, published_at, title, summary_hu, summary_en,
           embedding vector(1024), tsv tsvector generated always as (to_tsvector('hungarian', title || ' ' || summary_hu)) stored,
           cluster_id uuid)       -- dedup cluster
news_node (news_id, node_id, relevance real)
```

## 4. Users, AOIs, interests

```sql
app_user (id uuid pk, entra_oid text unique, locale text default 'hu', created_at)
user_interest (user_id, node_id, role text check (role in ('producer','buyer','processor','trader','advisor')),
               organic boolean, primary key (user_id, node_id, role))
aoi (id uuid pk, user_id, name, geom geometry(MultiPolygon, 4326), nuts3 text, created_at)
indicator_value (aoi_id, indicator text, valid_time timestamptz, value real, run_id, primary key (aoi_id, indicator, valid_time, run_id))

alert_rule (id uuid pk, user_id, kind text,   -- price_cross | pct_move | crowd_available | weather | release | news
            node_id null, series_id null, aoi_id null, indicator null,
            op text, threshold numeric, channel text[], active boolean)      -- BP-12
notification (id uuid pk, user_id, rule_id null, channel, sent_at, opened_at, muted boolean)
notification_pref (user_id pk, digest_day int, push_cap_week int default 2, quiet_hours int4range)  -- BP-35
outcome (id uuid pk, user_id, node_id, kind text, value numeric, period date)  -- private ROI ledger (BP-30)
subscription (user_id, tier text, valid_until, source text)  -- free | pro | contributor | b2b
```

## 5. User intel (Phase 4, legal gate)

```sql
offer (id uuid pk, user_id, side text check (side in ('offer','bid')), node_id, quality jsonb,
       quantity numeric, unit, price numeric null, nuts3 text, valid_until date, status text)
price_report (id uuid pk, reporter_hash text, node_id, market_stage, direction text,  -- bought | sold
              quality jsonb, nuts3, period date, value numeric, volume numeric, created_at,
              verified boolean default false,        -- invoice checked, file deleted after (BP-18)
              status text default 'held',            -- held | accepted | rejected (BP-21)
              flags text[], weight real)             -- evidence, freshness, reputation (BP-19)
peer_check (report_scope text, user_id, answer text, created_at)   -- "about right?" (BP-20)
reputation (user_id pk, score real, reports_accepted int, reports_rejected int)
access_grant (user_id, reason text, valid_until date)   -- give-to-get unlock (BP-17)
-- crowd price: published only when distinct reporters >= k, lagged one period, banded
create materialized view crowd_price as
  select node_id, market_stage, period, percentile_cont(array[0.25,0.5,0.75]) within group (order by value) as bands,
         count(distinct reporter_hash) as n
  from price_report where period < date_trunc('week', now())
  group by 1,2,3 having count(distinct reporter_hash) >= 5;
```

The view above is the minimum. The production aggregator is a job (not a view) that also applies:
status = accepted only, weights, median/MAD trimming, dominance (no reporter > 25 % of volume)
or p% rule, secondary suppression across region/product totals, hierarchical fallback
county → NUTS2 → HU, and writes results as `observation` rows with
`evidence_type = community_report` and `n_reporters` (BP-8, BP-22).

Location is stored at NUTS3 only (no coordinates) for offers and reports.

## 6. Operations

```sql
job_run (id uuid pk, job text, started_at, finished_at, status, rows_in, rows_out, error text)
```
