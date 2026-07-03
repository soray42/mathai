"""Build the math->AI citation subgraph from OpenAlex.

Starts from an AI/CS seed set, walks referenced_works to pull in the
mathematical ancestry, and writes a pinned edge list. The snapshot date
in configs/data_versions.yaml is stamped onto every row so the graph can
be rebuilt exactly.
"""
from pathlib import Path


def fetch_seed_set(concepts, year_range):
    """Return work ids for the AI/CS seed papers we start the walk from."""
    # TODO: page through the OpenAlex works endpoint, filter by concept + year
    raise NotImplementedError


def expand_references(seed_ids, max_depth):
    """Follow referenced_works from the seed set to collect math ancestors."""
    # TODO: breadth-first over referenced_works, stop at max_depth
    raise NotImplementedError


def write_edges(edges, out_path: Path):
    """Persist the directed edge list (citing -> cited) as parquet."""
    # TODO: columns = src_id, dst_id, edge_weight, plus the pinned data_version
    raise NotImplementedError


if __name__ == "__main__":
    pass
