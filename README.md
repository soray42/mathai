# mathai

Measuring how mathematics is consumed by AI/CS research: an effective-age
spectrum on the citation graph and a cohort-level adoption-hazard model.

## What this measures

Two quantities over the mathematics -> AI citation graph:

- **Effective age `A(p)`** — a recursive age for each paper,
  `A = (1-lambda)*birth + lambda*W*A`, solved as the linear system
  `(I - lambda*W) A = (1-lambda) birth`. It captures how far back into the
  mathematical literature a piece of AI work is effectively reaching.
- **Adoption hazard** — a survival model (with a cure fraction for
  mathematics that is never adopted) for how quickly a mathematical
  concept is first put to substantive use in an AI subdomain, compared
  cohort by cohort.

A concept's first appearance is dated two independent ways — from the
citation graph and from full text — and the two are compared rather than
merged, since where they disagree is informative.

## Pipeline

| Stage | Directory | Purpose |
|-------|-----------|---------|
| C1 | `src/c1_acquire` | Build the pinned citation subgraph, attach MSC labels, stream peS2o into a concept-by-year index |
| C2 | `src/c2_ap` | Solve `A(p)` across the lambda grid; date concepts from full text |
| C3 | `src/c3_hazard` | Define cohorts, detect first-use events, fit the cure survival model |
| C4 | `src/c4_main` | Cohort-trend estimate with the three-tier inflation correction |
| C5 | `src/c5_robust` | Lambda curve, subdomain stratification, null models, specification curve |
| C6 | `src/c6_output` | Exhibits and figures |

## Storage

The full peS2o corpus is never stored. It is streamed shard by shard and
reduced to a concept-by-year frequency index; everything on disk stays
well under a modest budget. Data directories under `data/` are
gitignored — only the pinned snapshot identifiers in
`configs/data_versions.yaml` are versioned.

## Reproducibility

Data snapshots are pinned in `configs/data_versions.yaml`, seeds live in
`configs/seeds.yaml`, and the lambda grid is fixed in
`configs/lambda_grid.yaml`. Python and R environments are declared in
`requirements.txt` and `renv.lock`.

## Layout

```
src/         pipeline stages c1..c6
configs/     pinned data versions, lambda grid, seeds
data/        raw / interim / processed  (gitignored)
outputs/     figures, tables, exhibits  (gitignored)
```
