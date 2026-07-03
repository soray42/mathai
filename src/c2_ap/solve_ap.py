"""Solve the effective-age spectrum A(p) on the citation DAG.

A = (1-lambda)*y + lambda*W*A, i.e. (I - lambda*W) A = (1-lambda) y.
W is row-stochastic and 0<lambda<1, so (I - lambda*W) is strictly
diagonally dominant: the iterative solve always converges, and the
Neumann series A = (1-lambda) sum_k (lambda*W)^k y gives a matrix-free
fixed-point iteration that needs only sparse mat-vec products. The whole
lambda grid reuses the same W.
"""
import numpy as np
from scipy.sparse import eye
from scipy.sparse.linalg import gmres


def solve_single_lambda(W, birth, lam, method="neumann", tol=1e-10,
                        max_iter=1000):
    """Return A(p) for one lambda.

    method='neumann' runs the fixed-point iteration A <- (1-lam)y + lam W A
    (robust, matrix-free); method='gmres' solves the sparse system directly.
    """
    birth = np.asarray(birth, dtype=np.float64)
    # Leaves (out-degree zero) are the oldest ancestors on a lineage: they
    # have no references of their own, so their effective age must stay at
    # their own birth year. Without pinning, the (1-lam)*birth term alone
    # shrinks a leaf toward zero and that error propagates down every chain
    # that passes through it, blowing up the effective age of its citers.
    is_leaf = np.asarray(W.sum(axis=1)).ravel() == 0
    if method == "gmres":
        n = W.shape[0]
        # Pin leaves inside the system, not after it: replace each leaf row of
        # (I - lam*W) with the identity row and set its right-hand side to the
        # leaf's birth year, so A[leaf]=birth[leaf] is enforced during the solve
        # and never propagates a shrunk value to the papers that cite it.
        A_op = (eye(n, format="csr") - lam * W).tolil()
        rhs = (1.0 - lam) * birth
        leaf_rows = np.flatnonzero(is_leaf)
        for j in leaf_rows:
            A_op.rows[j] = [j]
            A_op.data[j] = [1.0]
        rhs[is_leaf] = birth[is_leaf]
        x, _ = gmres(A_op.tocsr(), rhs, rtol=tol, maxiter=max_iter)
        return x
    a = birth.copy()
    for _ in range(max_iter):
        a_next = (1.0 - lam) * birth + lam * (W @ a)
        a_next[is_leaf] = birth[is_leaf]
        if np.max(np.abs(a_next - a)) < tol:
            return a_next
        a = a_next
    return a


def sweep_lambda(W, birth, lambda_grid, method="neumann"):
    """Solve across the lambda grid; returns dict lambda -> A(p) vector."""
    return {lam: solve_single_lambda(W, birth, lam, method=method)
            for lam in lambda_grid}


def effective_age(A_p, birth, ref_year):
    """Convert absolute effective birth-year A(p) into an age in years:
    how far back, on average, a paper's mathematical lineage reaches."""
    return np.asarray(ref_year, dtype=np.float64) - np.asarray(A_p)
