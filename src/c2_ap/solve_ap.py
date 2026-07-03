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
    if method == "gmres":
        n = W.shape[0]
        A_op = eye(n, format="csr") - lam * W
        x, _ = gmres(A_op, (1.0 - lam) * birth, rtol=tol, maxiter=max_iter)
        return x
    a = birth.copy()
    for _ in range(max_iter):
        a_next = (1.0 - lam) * birth + lam * (W @ a)
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
