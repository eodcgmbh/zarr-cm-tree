"""Interim ``dggs:`` attributes for the in-progress DGGS-in-Zarr convention."""

from __future__ import annotations

from typing import Any, Final

__all__ = [
    "DGGS_NAMESPACE",
    "build_dggs_attrs",
]

DGGS_NAMESPACE: Final = "dggs:"
"""Prefix used for the in-progress DGGS-in-Zarr convention.

The convention is *Under Consideration* on geozarr.org (repo
``zarr-conventions/dggs``); no UUID or JSON Schema is published yet.  When v1
ships, attribute keys produced by :func:`build_dggs_attrs` need a mechanical
rename only.
"""


def build_dggs_attrs(
    grid_name: str,
    level: int,
    indexing_scheme: str,
) -> dict[str, Any]:
    """Build interim ``dggs:`` attributes.

    Until the convention ships, this only namespaces the ``grid_name`` /
    ``level`` / ``indexing_scheme`` keys — there is no ``zarr_cm.dggs`` module
    to delegate to and no ``zarr_conventions`` entry to register.

    Parameters
    ----------
    grid_name : str
        DGGS family identifier (e.g. ``"healpix"``).
    level : int
        Refinement level / zoom.  Coerced with ``int()`` so numpy integers do
        not reach the store as non-JSON-serialisable attribute values.
    indexing_scheme : str
        Cell indexing scheme (e.g. ``"nested"``).

    Returns
    -------
    dict
        ``{"dggs:grid_name": ..., "dggs:level": ..., "dggs:indexing_scheme": ...}``.

    """
    return {
        f"{DGGS_NAMESPACE}grid_name": grid_name,
        f"{DGGS_NAMESPACE}level": int(level),
        f"{DGGS_NAMESPACE}indexing_scheme": indexing_scheme,
    }
