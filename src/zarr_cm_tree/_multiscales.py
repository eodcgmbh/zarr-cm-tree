"""GeoZarr ``multiscales`` layout attributes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from zarr_cm import multiscales as _zcm_multiscales
from zarr_cm.multiscales import LayoutObject, Transform

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

__all__ = [
    "LayoutObject",
    "Transform",
    "build_multiscales_attrs",
]


def build_multiscales_attrs(
    layout: Sequence[Mapping[str, Any]],
    *,
    resampling_method: str | None = None,
) -> dict[str, Any]:
    """Build ``multiscales`` convention attributes.

    Parameters
    ----------
    layout : Sequence[Mapping[str, Any]]
        One entry per pyramid level.  Each entry is a mapping with ``asset``
        (path to the sibling Zarr array / group) and optional ``derived_from``,
        ``transform``, and ``resampling_method``.  Plain dicts are accepted and
        checked at runtime; :class:`LayoutObject` is the typed shape.
    resampling_method : str or None, optional
        Top-level default resampling method (overridable per level).

    Returns
    -------
    dict
        ``{"multiscales": {...}}``.  No ``zarr_conventions`` entry (see
        :func:`~zarr_cm_tree.build_zarr_conventions`).

    Raises
    ------
    ValueError
        If *layout* is empty, an entry has no ``asset``, or an entry has
        ``derived_from`` without a ``transform``.

    """
    levels = _validate_layout(layout)
    if not levels:
        msg = "multiscales layout must have at least one level"
        raise ValueError(msg)
    ms = _zcm_multiscales.create(layout=levels, resampling_method=resampling_method)
    return {"multiscales": dict(ms)}


def _validate_layout(levels: Iterable[Mapping[str, Any]]) -> list[LayoutObject]:
    """Validate and copy layout entries, enforcing the rules zarr_cm does not."""
    out: list[LayoutObject] = []
    for entry in levels:
        if "asset" not in entry:
            msg = "every multiscales layout entry must have an 'asset' key"
            raise ValueError(msg)
        if "derived_from" in entry and "transform" not in entry:
            msg = "multiscales layout entry has 'derived_from' but no 'transform'"
            raise ValueError(msg)
        out.append(cast("LayoutObject", dict(entry)))
    return out
