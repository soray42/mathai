"""Stream peS2o and reduce it to a compact concept-by-year frequency index.

The full corpus is hundreds of GB and is never stored. We load it with
streaming=True, tally concept mentions per publication year one shard at
a time, discard each shard, and keep only the frequency index (~0.5 GB).
This is what keeps the whole project under the 50 GB storage budget.
"""
from pathlib import Path


def stream_shards(dataset_name="allenai/peS2o", revision="v2"):
    """Yield documents one shard at a time without materialising the corpus."""
    # TODO: datasets.load_dataset(..., streaming=True); iterate, never cache
    raise NotImplementedError


def tally_concepts(doc, vocabulary):
    """Count normalised concept mentions in a single document."""
    raise NotImplementedError


def write_frequency_index(counts, out_path: Path):
    """Persist the concept x year count table — the only durable output."""
    raise NotImplementedError


if __name__ == "__main__":
    pass
