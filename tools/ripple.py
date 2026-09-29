"""Propagate a shock through the agribusiness input/output network.

Deliberately simple, explainable heuristics (v0.1) meant to produce
"who gets hit, through what, and roughly when" rather than forecasts.

Usage:
    python tools/ripple.py drought
    python tools/ripple.py foot_and_mouth --lang hu
    python tools/ripple.py --list
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import yaml

MODEL = Path(__file__).resolve().parents[1] / "taxonomy" / "agribusiness_io.yaml"
DAMPING = 0.5        # share of a disturbance passed on per hop
THRESHOLD = 0.3      # ignore effects weaker than this
MAX_HOPS = 6


@dataclass
class Effect:
    cost: float = 0.0        # + = input costs up
    revenue: float = 0.0     # + = selling prices up
    capacity: float = 0.0    # - = output volume down
    hop: int | None = None
    month: int | None = None
    via: list[str] = field(default_factory=list)

    def touch(self, hop: int, month: int, via: str) -> None:
        if self.hop is None or hop < self.hop:
            self.hop, self.month = hop, month
        if via not in self.via:
            self.via.append(via)


def load(path: Path = MODEL) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_index(model: dict):
    producers, consumers = defaultdict(dict), defaultdict(dict)
    for b, spec in model["agribusinesses"].items():
        for p, w in spec.get("outputs", {}).items():
            producers[p][b] = w
        for p, w in spec.get("inputs", {}).items():
            consumers[p][b] = w
    return producers, consumers


def propagate(model: dict, shock_id: str) -> dict[str, Effect]:
    shock = model["shocks"][shock_id]
    biz, prods = model["agribusinesses"], model["products"]
    producers, consumers = build_index(model)
    effects: dict[str, Effect] = defaultdict(Effect)

    def external(p: str) -> bool:
        return prods[p].get("origin") == "external"

    def unpriced(p: str) -> bool:
        return prods[p].get("payment") == "none"

    # frontier items: (kind, key, magnitude, hop, month, label, propagate_demand)
    #   supply:   product availability change (neg = scarcer)
    #   demand:   product demand change (neg = less demand)
    #   price:    direct price change of an (external) product
    #   capacity: business output change (neg = less output)
    frontier = []
    for p, v in shock.get("supply", {}).items():
        frontier.append(("supply", p, v, 0, 0, shock_id, True))
        # direct producers lose volume at hop 0
        for b, w in producers.get(p, {}).items():
            e = effects[b]
            e.capacity += v * w / 3
            e.touch(0, 0, f"{shock_id}: {p}")
    for p, v in shock.get("price", {}).items():
        frontier.append(("price", p, v, 0, 0, shock_id, True))
    for b, v in shock.get("capacity", {}).items():
        frontier.append(("capacity", b, v, 0, 0, shock_id, True))
    for p in shock.get("trade_ban", []):
        frontier.append(("demand", p, -2, 0, 0, f"export ban on {p}", True))

    seen = set()
    while frontier:
        kind, key, mag, hop, month, label, prop_demand = frontier.pop(0)
        if abs(mag) < THRESHOLD or hop > MAX_HOPS:
            continue
        sig = (kind, key, round(mag, 1), hop)
        if sig in seen:
            continue
        seen.add(sig)

        if kind == "capacity":
            e = effects[key]
            e.capacity += mag
            e.touch(hop, month, label)
            cycle = biz[key].get("cycle_months", 1)
            for p, w in biz[key].get("outputs", {}).items():
                frontier.append(("supply", p, mag * w / 3, hop + 1, month + cycle, f"{key} → {p}", True))
            if prop_demand:
                for p, w in biz[key].get("inputs", {}).items():
                    if not external(p):
                        frontier.append(("demand", p, mag * w / 3, hop + 1, month,
                                         f"{key} buys less {p}" if mag < 0 else f"{key} buys more {p}", True))
            continue

        price = {"supply": -mag, "demand": mag, "price": mag}[kind]
        for b, w in consumers.get(key, {}).items():
            if b in shock.get("capacity", {}):
                continue
            e = effects[b]
            if not unpriced(key):
                e.cost += price * w / 3
            e.touch(hop + 1, month, f"{key} {'scarcer' if kind == 'supply' and mag < 0 else ('dearer' if price > 0 else 'cheaper')}")
            if kind == "supply" and mag < 0 and w == 3:
                # physical shortage of a critical input; no extra demand signal (same scarcity)
                frontier.append(("capacity", b, mag * DAMPING, hop + 1, month, f"short of {key}", False))
            elif kind == "price" and price > 0 and w == 3:
                frontier.append(("capacity", b, -price * DAMPING / 2, hop + 1, month, f"{key} too costly", True))
        if unpriced(key) or kind == "price":
            continue
        for b, w in producers.get(key, {}).items():
            if b in shock.get("capacity", {}):
                continue
            e = effects[b]
            e.revenue += price * w / 3
            e.touch(hop + 1, month, f"{key} price {'up' if price > 0 else 'down'}")

    return dict(effects)


def fmt(v: float) -> str:
    if abs(v) < THRESHOLD:
        return "·"
    return ("↑" if v > 0 else "↓") * min(3, max(1, round(abs(v))))


def report(model: dict, shock_id: str, lang: str = "en") -> str:
    effects = propagate(model, shock_id)
    biz = model["agribusinesses"]
    rows = sorted(effects.items(), key=lambda kv: (kv[1].hop or 0, -abs(kv[1].capacity) - abs(kv[1].cost)))
    title = model["shocks"][shock_id][lang]
    out = [f"Shock: {title}", "",
           f"{'hop':>3} {'~mo':>4}  {'agribusiness':<42} {'costs':>5} {'price':>5} {'output':>6}  via"]
    for b, e in rows:
        if max(abs(e.cost), abs(e.revenue), abs(e.capacity)) < THRESHOLD:
            continue
        out.append(f"{e.hop:>3} {e.month:>4}  {biz[b][lang]:<42} {fmt(e.cost):>5} "
                   f"{fmt(e.revenue):>5} {fmt(e.capacity):>6}  {', '.join(e.via[:3])}")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("shock", nargs="?")
    ap.add_argument("--lang", default="en", choices=["en", "hu"])
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    model = load()
    if args.list or not args.shock:
        for k, v in model["shocks"].items():
            print(f"{k:<22} {v[args.lang]}")
        return
    print(report(model, args.shock, args.lang))


if __name__ == "__main__":
    main()
