"""GeoZarr convention attribute builders.

An opinionated bridge between :mod:`pyproj` and :mod:`zarr_cm`: it produces the
plain attribute dicts that make up the ``attributes`` block of a Zarr v3 group
or array for the GeoZarr conventions ``proj:``, ``spatial:`` and
``multiscales``, plus an interim ``dggs:`` placeholder.

:mod:`zarr_cm` owns the conventions themselves (schemas, validation, revisions,
registry entries).  This package adds what it deliberately does not: a
canonical :class:`pyproj.CRS` that knows how to serialise itself, domain
defaults for gridded data, layout rules the schema does not encode, and
:func:`geozarr_attrs` to emit several conventions at once with a matching
``zarr_conventions`` registry.

Everything returned is a plain ``dict``, never a model, so it can be merged
straight into ``xarray.Dataset.attrs``.

References
----------
* https://geozarr.org/conventions
* https://github.com/zarr-conventions/zarr-cm

"""

from __future__ import annotations

from zarr_cm_tree._attrs import geozarr_attrs
from zarr_cm_tree._conventions import (
    MULTISCALES_UUID,
    PROJ_UUID,
    SPATIAL_UUID,
    build_zarr_conventions,
    convention_metadata,
    current_revisions,
    merge_attrs,
)
from zarr_cm_tree._dggs import DGGS_NAMESPACE, build_dggs_attrs
from zarr_cm_tree._multiscales import (
    LayoutObject,
    Transform,
    build_multiscales_attrs,
)
from zarr_cm_tree._proj import GeoZarrProj, GeoZarrProjFormat, build_proj_attrs
from zarr_cm_tree._spatial import GeoZarrSpatial, build_spatial_attrs

__all__ = [
    "DGGS_NAMESPACE",
    "MULTISCALES_UUID",
    "PROJ_UUID",
    "SPATIAL_UUID",
    "GeoZarrProj",
    "GeoZarrProjFormat",
    "GeoZarrSpatial",
    "LayoutObject",
    "Transform",
    "build_dggs_attrs",
    "build_multiscales_attrs",
    "build_proj_attrs",
    "build_spatial_attrs",
    "build_zarr_conventions",
    "convention_metadata",
    "current_revisions",
    "geozarr_attrs",
    "merge_attrs",
]
