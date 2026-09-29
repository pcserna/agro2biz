# `tools/price_transmission.py` – design spec

Input: price moves in percent for products or benchmarks.
Output: per-business cost change, break-even price change, expected price change,
margin squeeze, and the margin indicators from `price_links.yaml`, in hu or en.

```
python tools/price_transmission.py maize_grain=+20 natural_gas=+50
python tools/price_transmission.py --benchmark ttf_gas=+80 --lang hu
python tools/price_transmission.py --scenario energy_price_spike   # reuse ripple shocks with a price block
```

## 1. Notation

- `x_p` – log price change of product *p* (use `ln(1 + pct/100)`; report back as %).
- `a_{b,p}` – cost share of input *p* in business *b* (`cost_structure.shares`); `Σ_p a_{b,p} ≤ 1`.
- `π_b` – pass-through of business *b* (`pass_through.by_sector[sector(b)]`, else `default`).
- `w_{b,p}` – output weight of product *p* for business *b* (from `agribusiness_io.yaml`, 1–3).
- `E` – exogenous set: products the user shocked, plus products driven by a shocked benchmark.

## 2. Algorithm

1. **Benchmarks → products.** For each shocked benchmark `k` with move `m_k` and
   `drives: {p: e}`, add `e · m_k` to `x_p` and put *p* in `E`. `*tradable` expands to
   every product with `tradable: true`. Lags are reported, not simulated (v1).

2. **Cost push (Leontief-style fixed point).** Iterate until `max |Δx| < 1e-6` or 100 steps:

   ```
   c_b  = Σ_p a_{b,p} · x_p                       # break-even price change of b's output
   x_p  = Σ_b s_{b,p} · π_b · c_b    for p ∉ E     # expected price change of p
   ```

   where `s_{b,p} = w_{b,p} / Σ_{b'} w_{b',p}` splits a product across its producers
   (only producers that have a cost structure count).
   Convergence: every update is a non-negative combination with total weight
   `max_b π_b · Σ_p a_{b,p} < 1`, so the map is a contraction. The test suite asserts this bound.

3. **Substitutes.** After the fixed point, for each group with coefficient `γ` and each
   member *q* ∉ E: `x_q += γ · mean(x_r for r in group, r ≠ q, |x_r| > 0)`.
   Then run step 2 again (one outer loop, max 5 rounds) so substitutes feed back into costs.
   Report which moves came from substitution.

4. **Co-products.** For each process with `input` *i* and `yields` `y_j`:
   gross margin change ≈ `Σ_j v_j · x_j − v_i · x_i`, with value weights `v` from
   reference prices (`taxonomy/reference_prices.yaml`, new file, `status: prior`).
   Without reference prices, report the direction only.
   `dairy_herd` (no input): report output value change only.

5. **Margin squeeze per business.** `m_b = Σ_p s'_{b,p} · x_p − c_b`, where `s'` are
   output revenue shares (normalised output weights). Negative = margin squeezed.
   Example: with π = 0.2, a +10 % break-even push gives a +2 % expected price, so the margin shrinks by about 8 % of the output price.

6. **Margin indicators.** Ratios `num/den`: change = `x_num − x_den`.
   Crush and ethanol margins come from step 4.

## 3. Output (mirrors `ripple.py`)

```
Price moves: natural_gas +50%

business                     cost   break-even  expected  margin   via
Fertilizer plant            +35.5%    +35.5%     +31.5%   -3.0%   natural_gas
Arable crop farm             +6.5%     +6.5%      +1.3%   -4.9%   fertilizer_n, natural_gas
...

Margin indicators
Wheat-to-fertilizer ratio    -23%   ▼▼▼
```

Numbers are shown with one decimal and a `prior` badge; `--json` emits the same data for the API.

## 4. Module layout

- `packages/agromodels/loader.py` – loads and cross-validates both YAMLs (shared with ripple).
- `packages/agromodels/transmission.py` – pure functions, no I/O: `apply_benchmarks`, `fixed_point`, `substitutes`, `co_product_margins`, `margins`.
- `tools/price_transmission.py` – CLI, formatting, `--lang`, `--json`.

## 5. Tests

- Reference integrity (every key exists in `products` / `agribusinesses`).
- Shares ≤ 1 per business; contraction bound `< 1`.
- Zero shock → zero everywhere.
- Linearity for small shocks: effect(2·s) ≈ 2·effect(s) before substitutes.
- Gas +50 % → fertilizer plant break-even = exp(0.75·ln 1.5) − 1 ≈ +35.5 % (hand check).
- Maize +20 % raises compound feed, pig/broiler costs, lowers pig-to-feed ratio.
- Exogenous products are never overwritten by the iteration.
