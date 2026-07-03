"""Pilot: effective-age spectrum on the optimal-transport x AI subdomain.

Reproduces the two-panel A(p) figure from the pilot run -- how the effective
consumption age grows as lambda puts more weight on ancestral lineage, and the
fat right tail of that distribution. This is the descriptive C1 result on the
strong-signal subdomain, kept separate from the cohort-trend claim.

Inputs (pulled into data/interim/, see configs/data_versions.yaml):
  pilot_seed_ot.json    seed OT x AI papers with referenced_works + year
  pilot_ref_meta.json   reference metadata (publication year)
  pilot_ref_labels.json per-reference math / non-math label

Run from anywhere; paths resolve relative to the repo root.
"""
import json
import random
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from c2_ap.build_math_dag import build_adjacency, row_normalise
from c2_ap.solve_ap import solve_single_lambda

REPO = Path(__file__).resolve().parents[2]
INTERIM = REPO / "data" / "interim"
FIGDIR = REPO / "outputs" / "figures"

# Pilot sample: fixed seed and size so the figure reproduces exactly.
SAMPLE_SEED = 20240601
SAMPLE_N = 300
LAMBDA_GRID = np.round(np.arange(0.0, 0.96, 0.05), 2)


def load_pilot():
    seed = json.load(open(INTERIM / "pilot_seed_ot.json"))
    ref_meta = json.load(open(INTERIM / "pilot_ref_meta.json"))
    ref_label = json.load(open(INTERIM / "pilot_ref_labels.json"))
    return seed, ref_meta, ref_label


def build_subgraph(seed, ref_meta, ref_label):
    """Sample seeds, keep only edges into math references, return W and years."""
    random.seed(SAMPLE_SEED)
    sub = random.sample(seed, SAMPLE_N)

    math_refs = {rid for rid, lab in ref_label.items() if lab == "math"}
    seed_ids = [w["id"] for w in sub]
    nodes = list(dict.fromkeys(seed_ids + sorted(math_refs)))
    idx = {n: i for i, n in enumerate(nodes)}
    edges = [(w["id"], r) for w in sub
             for r in (w.get("referenced_works") or []) if r in math_refs]

    seed_year = {w["id"]: w.get("publication_year") for w in sub}

    def year_of(nid):
        if seed_year.get(nid):
            return seed_year[nid]
        if nid in ref_meta and ref_meta[nid].get("year"):
            return ref_meta[nid]["year"]
        return None

    years = np.array([year_of(n) if year_of(n) else np.nan for n in nodes],
                     dtype=float)
    years = np.where(np.isnan(years), np.nanmedian(years), years)

    W = row_normalise(build_adjacency(edges, idx))
    seed_rows = np.array(sorted({idx[e[0]] for e in edges}))
    return W, years, seed_rows


def make_figure(W, years, seed_rows, out_path):
    means, medians, p90s = [], [], []
    for lam in LAMBDA_GRID:
        ap = solve_single_lambda(W, years, float(lam))
        ages = years[seed_rows] - ap[seed_rows]
        means.append(np.mean(ages))
        medians.append(np.median(ages))
        p90s.append(np.percentile(ages, 90))
    means, medians, p90s = map(np.array, (means, medians, p90s))

    d05 = years[seed_rows] - solve_single_lambda(W, years, 0.5)[seed_rows]
    d08 = years[seed_rows] - solve_single_lambda(W, years, 0.8)[seed_rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.8))
    ax1.plot(LAMBDA_GRID, means, '-o', color='#1f4e79', ms=4, label='mean')
    ax1.plot(LAMBDA_GRID, medians, '-s', color='#5a9e5a', ms=3, label='median')
    ax1.plot(LAMBDA_GRID, p90s, '-^', color='#c0662a', ms=3,
             label='90th percentile')
    ax1.set_xlabel(r'$\lambda$  (weight on ancestral lineage)')
    ax1.set_ylabel('effective consumption age (years)')
    ax1.set_title('Deeper lineage weighting lengthens effective age',
                  fontsize=8, loc='left')
    ax1.legend(frameon=False, fontsize=7)
    ax1.margins(0.04)

    bins = np.arange(0, 60, 3)
    ax2.hist(d05, bins=bins, alpha=0.6, color='#1f4e79', label=r'$\lambda=0.5$')
    ax2.hist(d08, bins=bins, alpha=0.5, color='#c0662a', label=r'$\lambda=0.8$')
    ax2.set_xlabel('effective consumption age (years)')
    ax2.set_ylabel('number of AI papers')
    ax2.set_title('Fat right tail: archaeological reach', fontsize=8, loc='left')
    ax2.legend(frameon=False, fontsize=7)
    ax2.margins(0.04)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    return fig


if __name__ == "__main__":
    seed, ref_meta, ref_label = load_pilot()
    W, years, seed_rows = build_subgraph(seed, ref_meta, ref_label)
    make_figure(W, years, seed_rows, FIGDIR / "pilot_ap_lambda.png")
