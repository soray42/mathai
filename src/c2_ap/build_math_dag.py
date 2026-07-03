"""Carve the pure-mathematical-ancestry subgraph and normalise edge flow.

Keeps only edges that lead toward *pure* mathematical ancestors -- math
that is not itself downstream of AI (see c1_acquire/provenance_filter).
Edges are oriented citing->cited and row-normalised, so textbook hubs with
many out-edges spread little weight along each one and cannot short-circuit
the recursion.
"""
import numpy as np
from scipy.sparse import csr_matrix


def build_adjacency(edges, node_index):
    """Assemble a sparse citing->cited adjacency from an edge list.

    edges: iterable of (src_id, dst_id). node_index: id -> row/col int.
    Returns a CSR matrix W_raw with unit entries on observed edges.
    """
    rows, cols = [], []
    for src, dst in edges:
        if src in node_index and dst in node_index:
            rows.append(node_index[src])
            cols.append(node_index[dst])
    n = len(node_index)
    data = np.ones(len(rows), dtype=np.float64)
    return csr_matrix((data, (rows, cols)), shape=(n, n))


def keep_math_ancestry_edges(adjacency, is_math_ancestor):
    """Zero out columns that are not pure mathematical ancestors.

    is_math_ancestor: boolean array aligned to node index. Only edges whose
    *target* is a pure ancestor are kept, so the recursion propagates age
    along genuine math lineage rather than reverse-flow references.
    """
    keep = np.asarray(is_math_ancestor, dtype=bool)
    W = adjacency.tocsc()
    for j in range(W.shape[1]):
        if not keep[j]:
            W.data[W.indptr[j]:W.indptr[j + 1]] = 0.0
    W.eliminate_zeros()
    return W.tocsr()


def row_normalise(adjacency):
    """Make each non-empty row sum to one so W is a transition matrix."""
    W = adjacency.tocsr().astype(np.float64)
    deg = np.asarray(W.sum(axis=1)).ravel()
    inv = np.zeros_like(deg)
    nz = deg > 0
    inv[nz] = 1.0 / deg[nz]
    from scipy.sparse import diags
    return diags(inv) @ W
