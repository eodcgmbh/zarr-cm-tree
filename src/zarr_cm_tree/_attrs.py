"""Combine several conventions into one attribute dict."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from zarr_cm_tree._conventions import build_zarr_conventions
from zarr_cm_tree._multiscales import build_multiscales_attrs

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from zarr_cm_tree._proj import GeoZarrProj
    from zarr_cm_tree._spatial import GeoZarrSpatial

__all__ = ["geozarr_attrs"]


def geozarr_attrs(
    *,
    crs: GeoZarrProj | None = None,
    spatial: GeoZarrSpatial | None = None,
    multiscales: Sequence[Mapping[str, Any]] | None = None,
    resampling_method: str | None = None,
) -> dict[str, Any]:
    """Build the attrs for any combination of conventions, plus their registry.

    The one-stop entry point for writing GeoZarr metadata onto a group: it emits
    the convention attributes and the matching ``zarr_conventions`` registry
    array, in a fixed ``proj`` -> ``spatial`` -> ``multiscales`` order, so the
    registry always describes exactly the conventions present.

    Parameters
    ----------
    crs : GeoZarrProj or None, optional
        CRS to emit as ``proj:*``.
    spatial : GeoZarrSpatial or None, optional
        Grid geometry to emit as ``spatial:*``.
    multiscales : Sequence[Mapping[str, Any]] or None, optional
        Pyramid layout entries (see :func:`build_multiscales_attrs`).  An empty
        sequence is treated as absent.
    resampling_method : str or None, optional
        Default resampling method for the ``multiscales`` block.

    Returns
    -------
    dict
        Merged attributes ready for ``group.attrs.update(...)``, with a
        ``zarr_conventions`` entry per active convention.  Empty when no
        convention is given.

    """
    attrs: dict[str, Any] = {}
    conventions: list[str] = []
    if crs is not None:
        attrs.update(crs.to_proj_attrs())
        conventions.append("proj")
    if spatial is not None:
        attrs.update(spatial.to_attrs())
        conventions.append("spatial")
    if multiscales:
        attrs.update(
            build_multiscales_attrs(multiscales, resampling_method=resampling_method)
        )
        conventions.append("multiscales")
    if conventions:
        attrs["zarr_conventions"] = build_zarr_conventions(*conventions)
    return attrs
