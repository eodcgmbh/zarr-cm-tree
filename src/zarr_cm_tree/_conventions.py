"""Convention registry, revision awareness, and attribute merging.

Each GeoZarr convention in :mod:`zarr_cm` ships at one or more numbered
*revisions*.  A revision fixes the convention's JSON Schema — which attribute
keys are legal, how strictly they are validated, and the ``schema_url`` written
into the ``zarr_conventions`` registry array of a store.

This package deliberately follows whatever revision the installed ``zarr_cm``
declares latest, rather than pinning one: a pin nobody updates goes stale, and
every store records the revision that wrote it in its own ``schema_url``, so
drift stays auditable after the fact.  Reads are unaffected either way —
``zarr_cm.<convention>.detect()`` sniffs the revision from the store.

The revisions in use are reported by :func:`current_revisions`, and
``tests/test_conventions.py`` asserts them, so a ``zarr_cm`` upgrade that ships
a new revision surfaces as one failing test rather than silently changing what
gets written.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from zarr_cm import multiscales as _zcm_multiscales
from zarr_cm import proj as _zcm_proj
from zarr_cm import spatial as _zcm_spatial

if TYPE_CHECKING:
    from types import ModuleType

_CONVENTIONS: Final[dict[str, ModuleType]] = {
    "proj": _zcm_proj,
    "spatial": _zcm_spatial,
    "multiscales": _zcm_multiscales,
}

_ALIASES: Final[dict[str, str]] = {"geo-proj": "proj"}
"""Accepted spellings that are not the canonical name.

Upstream renamed ``geo-proj`` to ``proj``; ``zarr_cm.ConventionName`` still
carries the old spelling, and so do stores written before the rename.
"""

PROJ_UUID: str = _zcm_proj.UUID
SPATIAL_UUID: str = _zcm_spatial.UUID
MULTISCALES_UUID: str = _zcm_multiscales.UUID


def _module(name: str) -> ModuleType:
    """Resolve *name* to its :mod:`zarr_cm` convention module."""
    resolved = _ALIASES.get(name, name)
    try:
        return _CONVENTIONS[resolved]
    except KeyError:
        msg = f"unknown GeoZarr convention: {name!r}"
        raise KeyError(msg) from None


def current_revisions() -> dict[str, str]:
    """Return the revision each convention is currently written at.

    Returns
    -------
    dict[str, str]
        Mapping from canonical convention name to the revision label the
        installed :mod:`zarr_cm` declares latest, e.g. ``{"proj": "r3", ...}``.

    """
    return {name: module.LATEST for name, module in _CONVENTIONS.items()}


def convention_metadata(name: str) -> dict[str, Any]:
    """Return the ``zarr_conventions`` registry entry for convention *name*.

    Parameters
    ----------
    name : str
        Convention name, e.g. ``"proj"`` (or its ``"geo-proj"`` alias),
        ``"spatial"``, ``"multiscales"``.

    Returns
    -------
    dict
        A copy of the ConventionMetadataObject, carrying its ``uuid``,
        ``schema_url``, ``spec_url``, ``name`` and ``description``.

    Raises
    ------
    KeyError
        If *name* is not a known GeoZarr convention.

    """
    return dict(_module(name).CMO)


def build_zarr_conventions(*names: str) -> list[dict[str, Any]]:
    """Build ``zarr_conventions`` registry entries for the given conventions.

    Parameters
    ----------
    *names : str
        Convention names, e.g. ``"proj"``, ``"spatial"``, ``"multiscales"``.

    Returns
    -------
    list[dict]
        One registry entry per name, in the order given.

    Raises
    ------
    KeyError
        If any name is not a known GeoZarr convention.

    """
    return [convention_metadata(name) for name in names]


def merge_attrs(*parts: dict[str, Any] | None) -> dict[str, Any]:
    """Merge attribute dicts left-to-right; later keys override earlier ones.

    ``None`` parts are skipped.
    """
    merged: dict[str, Any] = {}
    for part in parts:
        if part:
            merged.update(part)
    return merged
