"""Carve the mathematical-ancestry subgraph and normalise edge flow.

Keeps only edges that lead toward mathematical ancestors, orients them
citing->cited, and row-normalises the weights. Row normalisation is what
stops textbook hubs from short-circuiting the recursion: a hub with many
out-edges spreads little weight along each one.
"""


def keep_math_ancestry_edges(edges, msc_labels):
    """Drop edges that do not terminate in a mathematics-classified node."""
    raise NotImplementedError


def row_normalise(adjacency):
    """Make each row sum to one so W is a transition matrix."""
    raise NotImplementedError


if __name__ == "__main__":
    pass
