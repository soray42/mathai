"""Build the N=1560 stratified seed set and its reference metadata.

Samples 120 AI/CS papers per year over 2013-2025 (13 x 120 = 1560), keeping
the sampling deterministic through OpenAlex's sample+seed so the set rebuilds
exactly, then batch-fetches every 1-hop reference so the age model has a year
for each ancestor. Broadens the earlier single-subdomain pilot (OT x AI) to
the whole AI subfield, which is what the scale-up is meant to test: whether
the effective-age and adoption signals hold across the field rather than in
one strong-signal pocket.

Outputs, written under data/interim (gitignored):
  seed_set_n1560.json   the 1560 sampled seed works (full records)
  ref_meta_n1560.json   id -> reference work record for every 1-hop ancestor

Config comes from configs/seeds.yaml (sampling seed) and the year range and
per-year count below. Run:  PYTHONPATH=src python -m c1_acquire.build_seed_set
"""
import json
from pathlib import Path

import yaml

from c1_acquire.fetch_openalex import fetch_seed_set, expand_references

REPO = Path(__file__).resolve().parents[2]
INTERIM = REPO / "data" / "interim"
SEEDS_CFG = REPO / "configs" / "seeds.yaml"

YEAR_RANGE = (2013, 2025)
PER_YEAR = 120


def main():
    cfg = yaml.safe_load(open(SEEDS_CFG))
    sample_seed = cfg["sampling_seed"]

    print(f"sampling {PER_YEAR}/yr over {YEAR_RANGE} (seed={sample_seed})")
    seeds = fetch_seed_set(YEAR_RANGE, PER_YEAR, sample_seed)
    print(f"total seeds: {len(seeds)}")

    ref_ids = [r for w in seeds for r in (w.get("referenced_works") or [])]
    print(f"1-hop reference edges: {len(ref_ids)} "
          f"({len(set(ref_ids))} unique) -> fetching metadata")
    ref_meta = expand_references(ref_ids)
    print(f"reference works fetched: {len(ref_meta)}")

    INTERIM.mkdir(parents=True, exist_ok=True)
    json.dump(seeds, open(INTERIM / "seed_set_n1560.json", "w"))
    json.dump(ref_meta, open(INTERIM / "ref_meta_n1560.json", "w"))
    print("wrote seed_set_n1560.json + ref_meta_n1560.json")


if __name__ == "__main__":
    main()