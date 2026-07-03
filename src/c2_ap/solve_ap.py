"""Solve the effective-age spectrum A(p) on the citation DAG.

A = (1-lambda)*y + lambda*W*A, i.e. (I - lambda*W) A = (1-lambda) y.
Because W is row-stochastic and 0<lambda<1 the system is diagonally
dominant, so an iterative solve always converges; when the graph is
acyclic a topological forward-substitution is used instead. The whole
lambda grid is solved by reusing the same preconditioner.
"""
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import gmres


def solve_single_lambda(W: csr_matrix, birth: np.ndarray, lam: float):
    """Return A(p) for one lambda via (I - lambda W) A = (1-lambda) birth."""
    # TODO: assemble I - lam*W, call gmres with a Jacobi preconditioner
    raise NotImplementedError


def sweep_lambda(W, birth, lambda_grid):
    """Solve across the lambda grid, reusing structure between solves."""
    raise NotImplementedError


if __name__ == "__main__":
    pass
