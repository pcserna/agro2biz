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
  frequency text              -- weekly | monthly | daily
)
observation (series_id, period_start date, period_end date, value numeric,
             value_low numeric, value_high numeric, volume numeric,
             document_id, extracted_by text,  -- 'adapter' | 'llm:<version>' | 'user'
             confidence real, primary key (series_id, period_start))
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
```

## 5. User intel (Phase 4, legal gate)

```sql
offer (id uuid pk, user_id, side text check (side in ('offer','bid')), node_id, quality jsonb,
       quantity numeric, unit, price numeric null, nuts3 text, valid_until date, status text)
price_report (id uuid pk, reporter_hash text, node_id, market_stage, quality jsonb, nuts3,
              period date, value numeric, created_at)
-- crowd price: published only when distinct reporters >= k, lagged one period, banded
create materialized view crowd_price as
  select node_id, market_stage, period, percentile_cont(array[0.25,0.5,0.75]) within group (order by value) as bands,
         count(distinct reporter_hash) as n
  from price_report where period < date_trunc('week', now())
  group by 1,2,3 having count(distinct reporter_hash) >= 5;
```

Location is stored at NUTS3 only (no coordinates) for offers and reports.

## 6. Operations

```sql
job_run (id uuid pk, job text, started_at, finished_at, status, rows_in, rows_out, error text)
```
