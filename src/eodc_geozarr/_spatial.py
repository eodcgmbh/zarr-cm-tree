"""GeoZarr ``spatial:`` attributes for gridded data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from zarr_cm import spatial as _zcm_spatial

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = [
    "GeoZarrSpatial",
    "build_spatial_attrs",
]


@dataclass(frozen=True, slots=True)
class GeoZarrSpatial:
    """GeoZarr ``spatial:`` metadata for a gridded dataset.

    Parameters
    ----------
    transform : tuple[float, ...]
        6- (or 9-) element affine mapping ``(col, row) -> (X, Y)``.
    dims : tuple[str, ...], optional
        Spatial dimension names in storage order.  Default ``("y", "x")``.
    shape : tuple[int, ...] or None, optional
        Pixel shape along ``dims``.
    bbox : tuple[float, ...] or None, optional
        ``(xmin, ymin, xmax, ymax)`` in the group's CRS.
    registration : str, optional
        ``"pixel"`` (centre) or ``"node"``.  Default ``"pixel"``.
    transform_type : str or None, optional
        Transform type tag; defaults to ``"affine"`` when ``transform`` is set.

    """

    transform: tuple[float, ...]
    dims: tuple[str, ...] = ("y", "x")
    shape: tuple[int, ...] | None = None
    bbox: tuple[float, ...] | None = None
    registration: str = "pixel"
    transform_type: str | None = None

    def to_attrs(self) -> dict[str, Any]:
        """Build ``spatial:*`` convention attributes."""
        return build_spatial_attrs(
            self.dims,
            transform=self.transform,
            shape=self.shape,
            bbox=self.bbox,
            registration=self.registration,
            transform_type=self.transform_type,
        )


def build_spatial_attrs(
    dimensions: Sequence[str],
    *,
    transform: Sequence[float] | None = None,
    shape: Sequence[int] | None = None,
    bbox: Sequence[float] | None = None,
    transform_type: str | None = None,
    registration: str = "pixel",
) -> dict[str, Any]:
    """Build ``spatial:`` convention attributes.

    Parameters
    ----------
    dimensions : Sequence[str]
        Names of the spatial dimensions in storage order (e.g. ``["y", "x"]``).
    transform : Sequence[float] or None, optional
        6- or 9-element affine pixel->world transform.
    shape : Sequence[int] or None, optional
        Spatial shape (length must match ``dimensions``).
    bbox : Sequence[float] or None, optional
        4- or 6-element bounding box in CRS coordinates.
    transform_type : str or None, optional
        Optional transform-type tag (e.g. ``"affine"``).  Defaults to
        ``"affine"`` when *transform* is given.
    registration : str, optional
        Pixel registration, ``"pixel"`` (centre) or ``"node"``.

    Returns
    -------
    dict
        Attributes dict with the ``spatial:*`` keys.

    Raises
    ------
    ValueError
        If *dimensions* is empty.

    """
    if not dimensions:
        msg = "spatial:dimensions must be non-empty"
        raise ValueError(msg)
    if transform is not None and transform_type is None:
        transform_type = "affine"
    return dict(
        _zcm_spatial.create(
            dimensions=list(dimensions),
            transform=list(transform) if transform is not None else None,
            shape=list(shape) if shape is not None else None,
            bbox=list(bbox) if bbox is not None else None,
            transform_type=transform_type,
            registration=registration,
        )
    )
