"""Stratified 10% sample: for each (venue, year) stratum, take 10% of papers
(deterministic, seed=137). Transparent by design — the sampling fraction is explicit,
not a hidden cap. Small strata keep >=1 paper (ceil) so no venue-year drops out.

Input : data/interim/seeds_dblp_full.jsonl  (146519 papers, 41 venues, 2013-2025)
Output: data/interim/seeds_sample10.jsonl
"""
import json, math, random
from collections import defaultdict, Counter

FRAC = 0.10
SEED = 137
rows = [json.loads(l) for l in open("data/interim/seeds_dblp_full.jsonl")]
strata = defaultdict(list)
for r in rows:
    strata[(r["venue"], r["seed_year"])].append(r)

rng = random.Random(SEED)
out = []
for key in sorted(strata):
    papers = strata[key]
    n = max(1, math.ceil(len(papers) * FRAC))
    idx = list(range(len(papers)))
    rng.shuffle(idx)
    for i in idx[:n]:
        out.append(papers[i])

with open("data/interim/seeds_sample10.jsonl", "w") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print("full:", len(rows), "-> 10% sample:", len(out))
print("by layer:", dict(Counter(r["layer"] for r in out)))
print("by year:", dict(sorted(Counter(r["seed_year"] for r in out).items())))
est_hours = len(out) * 2 * 3.0 / 3600      # ~2 S2 calls/seed, ~3s each
print(f"est S2 time (serial 1req/s): ~{est_hours:.1f} h")
