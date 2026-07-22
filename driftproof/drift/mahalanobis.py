from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MahalanobisReference:
    mean: np.ndarray
    inv_cov: np.ndarray


def fit_reference(x: np.ndarray, *, ridge: float = 1e-3) -> MahalanobisReference:
    if x.ndim != 2 or x.shape[0] < 2:
        raise ValueError("x must be a 2D matrix with at least two rows")
    mean = x.mean(axis=0)
    cov = np.cov(x, rowvar=False)
    cov = np.atleast_2d(cov) + ridge * np.eye(x.shape[1])
    inv_cov = np.linalg.pinv(cov)
    return MahalanobisReference(mean=mean, inv_cov=inv_cov)


def score(reference: MahalanobisReference, x: np.ndarray) -> np.ndarray:
    delta = np.atleast_2d(x) - reference.mean
    return np.einsum("ij,jk,ik->i", delta, reference.inv_cov, delta)
