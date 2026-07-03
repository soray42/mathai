"""N=1560 full-domain effective-age spectrum (unfiltered provenance).

Rebuilds the A(p) effective-age figure on the scaled-up, cross-subdomain seed
set rather than the single OT x AI pilot pocket, to check whether the fat
right tail of the effective consumption age survives when the seeds span the
whole AI subfield.

This is a fast first look, so it uses ALL one-hop references to build the
DAG -- the pure-mathematics provenance filter (c1_acquire/provenance_filter)
has not been applied yet. The tail here therefore mixes genuine mathematical
ancestry with non-math references; the C1 stage will re-run this on the
filtered graph. Read the shape, not the absolute purity.

Inputs (data/interim, gitignored):
  seed_set_n1560.json   the 1560 sampled seeds
  ref_meta_n1560.json   id -> reference work record (year, ...)

Run:  PYTHONPATH=src python -m c6_output.n1560_ap_spectrum
"""
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from c2_ap.build_math_dag import build_adjacency, row_normalise
from c2_ap.solve_ap import solve_single_lambda

REPO = Path(__file__).resolve().parents[2]
INTERIM = REPO / "data" / "interim"
FIGDIR = REPO / "outputs" / "figures"

YEAR_MIN = 1800   # drop obviously bad years (OpenAlex has a few 1400-type rows)
LAMBDA_GRID = np.round(np.arange(0.0, 0.96, 0.05), 2)


def load():
    seeds = json.load(open(INTERIM / "seed_set_n1560.json"))
    meta = json.load(open(INTERIM / "ref_meta_n1560.json"))
    return seeds, meta


def build(seeds, meta):
    """Assemble the citing->cited DAG over seeds + their references."""
    seed_year = {w["id"]: w.get("publication_year") for w in seeds}
    ref_year = {rid: r.get("publication_year") for rid, r in meta.items()}

    def valid_year(y):
        return y if (y and y >= YEAR_MIN) else None

    seed_ids = [w["id"] for w in seeds]
    ref_ids = sorted(meta.keys())
    nodes = list(dict.fromkeys(seed_ids + ref_ids))
    idx = {n: i for i, n in enumerate(nodes)}

    edges = [(w["id"], r) for w in seeds
             for r in (w.get("referenced_works") or []) if r in idx]

    def year_of(nid):
        return valid_year(seed_year.get(nid)) or valid_year(ref_year.get(nid))

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

    d08 = years[seed_rows] - solve_single_lambda(W, years, 0.8)[seed_rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.8))
    ax1.plot(LAMBDA_GRID, means, '-o', color='#1f4e79', ms=4, label='mean')
    ax1.plot(LAMBDA_GRID, medians, '-s', color='#5a9e5a', ms=3, label='median')
    ax1.plot(LAMBDA_GRID, p90s, '-^', color='#c0662a', ms=3,
             label='90th percentile')
    ax1.set_xlabel(r'$\lambda$  (weight on ancestral lineage)')
    ax1.set_ylabel('effective consumption age (years)')
    ax1.set_title('N=1560 cross-domain: effective age vs lambda',
                  fontsize=8, loc='left')
    ax1.legend(frameon=False, fontsize=7)
    ax1.margins(0.04)

    bins = np.arange(0, 80, 3)
    ax2.hist(d08, bins=bins, alpha=0.7, color='#c0662a', label=r'$\lambda=0.8$')
    ax2.set_xlabel('effective consumption age (years)')
    ax2.set_ylabel('number of AI papers')
    ax2.set_title('Fat right tail at N=1560 (unfiltered refs)',
                  fontsize=8, loc='left')
    ax2.legend(frameon=False, fontsize=7)
    ax2.margins(0.04)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches='tight')

    return {
        "n_seeds_with_edges": int(len(seed_rows)),
        "mean_lam08": float(means[np.argmin(np.abs(LAMBDA_GRID - 0.8))]),
        "p90_lam08": float(p90s[np.argmin(np.abs(LAMBDA_GRID - 0.8))]),
        "tail_max_lam08": float(np.max(d08)),
        "frac_over_25y_lam08": float(np.mean(d08 > 25)),
    }


if __name__ == "__main__":
    seeds, meta = load()
    W, years, seed_rows = build(seeds, meta)
    stats = make_figure(W, years, seed_rows, FIGDIR / "n1560_ap_spectrum.png")
    print(json.dumps(stats, indent=2))
