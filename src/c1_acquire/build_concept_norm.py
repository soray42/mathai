"""Normalise concept synonyms so first-appearance dating is not fooled.

'Earth mover's distance', 'Wasserstein metric' and 'optimal transport'
are one concept under three names; leaving them split shifts a first-use
date by a decade. Seeds come from zbMATH MSC descriptions and Wikipedia
redirects, then embedding clusters, then a hand-checked gold sample.
"""


def seed_synonyms():
    """Dictionary seeds from MSC descriptions + redirect tables."""
    raise NotImplementedError


def cluster_by_embedding(terms):
    """Group near-duplicate terms that the seed dictionary missed."""
    raise NotImplementedError


def spot_check_gold(clusters):
    """Manual audit sample; feeds the F1 gate in the C1 pilot."""
    raise NotImplementedError


if __name__ == "__main__":
    pass
