"""Pilot: cohort adoption of mathematics, naive vs censoring-fair.

Reproduces the two-panel cohort figure from the pilot run. The left panel is
the naive median lag from a math cohort's birth to its first use in AI -- it
falls steeply for recent cohorts and looks like AI ignores old mathematics.
The right panel corrects for right-censoring by asking, within a fixed window,
what fraction of each cohort is adopted within `win` years of birth; only
cohorts old enough to have had the full window are counted. The corrected view
reverses the naive reading: recent mathematics is adopted faster, and the naive
decline is a censoring artefact.

Inputs (pulled into data/interim/, see configs/data_versions.yaml):
  survival_set.json     per-item {birth, event, time} survival records
  adoption_events.json  per-item {birth_year, lag} observed adoption lags

Run from anywhere; paths resolve relative to the repo root.
"""
import collections
import json
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[2]
INTERIM = REPO / "data" / "interim"
FIGDIR = REPO / "outputs" / "figures"

# End of the observation window: a cohort is only counted in the fair panel
# once it has had the full `WINDOW` years to be observed.
OBS_YEAR = 2026
WINDOW = 10
MIN_COHORT = 10   # minimum records for a decade to be plotted
MIN_NAIVE = 5     # minimum records for a naive median to be shown


def load_pilot():
    surv = json.load(open(INTERIM / "survival_set.json"))
    rows = json.load(open(INTERIM / "adoption_events.json"))
    return surv, rows


def cohort_series(surv, rows):
    naive = collections.defaultdict(list)
    for r in rows:
        naive[int(r["birth_year"] // 10 * 10)].append(r["lag"])

    fair = collections.defaultdict(lambda: [0, 0])
    for s in surv:
        if (OBS_YEAR - s["birth"]) >= WINDOW:
            d = int(s["birth"] // 10 * 10)
            fair[d][1] += 1
            if s["event"] == 1 and s["time"] <= WINDOW:
                fair[d][0] += 1

    decs = [d for d in sorted(fair) if fair[d][1] >= MIN_COHORT]
    naive_med = [np.median(naive[d]) if len(naive.get(d, [])) >= MIN_NAIVE
                 else np.nan for d in decs]
    fair_rate = [100 * fair[d][0] / fair[d][1] for d in decs]
    return decs, naive_med, fair_rate


def make_figure(decs, naive_med, fair_rate, out_path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.8, 3.9))
    ax1.plot(decs, naive_med, '-o', color='#b0392a', ms=5)
    ax1.set_xlabel('math birth decade')
    ax1.set_ylabel('median observed lag (years)')
    ax1.set_title('Naive lag: looks like old math is slow (censoring artefact)',
                  fontsize=7.5, loc='left')
    ax1.margins(0.05)

    ax2.plot(decs, fair_rate, '-o', color='#1f4e79', ms=5)
    ax2.set_xlabel('math birth decade')
    ax2.set_ylabel('% adopted within 10y of birth')
    ax2.set_title('Censoring-fair: AI adopts NEW math faster',
                  fontsize=7.5, loc='left')
    ax2.margins(0.05)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200, bbox_inches='tight')
    return fig


if __name__ == "__main__":
    surv, rows = load_pilot()
    decs, naive_med, fair_rate = cohort_series(surv, rows)
    make_figure(decs, naive_med, fair_rate, FIGDIR / "cohort_adoption.png")
