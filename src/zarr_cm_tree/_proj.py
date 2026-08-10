"""GeoZarr ``proj:`` attributes and the :mod:`pyproj` bridge."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import pyproj
from zarr_cm import proj as _zcm_proj

__all__ = [
    "GeoZarrProj",
    "GeoZarrProjFormat",
    "build_proj_attrs",
]


def build_proj_attrs(
    *,
    crs_code: str | None = None,
    wkt2: str | None = None,
    projjson: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build ``proj:*`` attributes via :mod:`zarr_cm`.

    Parameters
    ----------
    crs_code : str or None
        Authority code (e.g. ``"EPSG:27704"``).
    wkt2 : str or None
        WKT2 definition string.
    projjson : dict or None
        PROJJSON object.

    Returns
    -------
    dict
        ``{}`` if all arguments are ``None``; otherwise one of ``proj:code``,
        ``proj:wkt2``, or ``proj:projjson``.  No ``zarr_conventions`` entry (see
        :func:`~zarr_cm_tree.build_zarr_conventions`).  Prefer
        :class:`GeoZarrProj` for validated inputs.

    """
    if crs_code is None and wkt2 is None and projjson is None:
        return {}
    return dict(_zcm_proj.create(code=crs_code, wkt2=wkt2, projjson=projjson))


class GeoZarrProjFormat(StrEnum):
    """GeoZarr ``proj:*`` encoding to emit from a :class:`pyproj.CRS`."""

    CODE = "code"
    WKT2 = "wkt2"
    PROJJSON = "projjson"


@dataclass(frozen=True, slots=True)
class GeoZarrProj:
    """A CRS held as a canonical :class:`pyproj.CRS`, serialisable to ``proj:*``.

    Parameters
    ----------
    crs : pyproj.CRS
        Parsed coordinate reference system.
    crs_format : GeoZarrProjFormat, optional
        How :meth:`to_proj_attrs` serialises ``crs`` (default ``code``).
        Authority codes are used when available; otherwise WKT2 is emitted.

    """

    crs: pyproj.CRS
    crs_format: GeoZarrProjFormat = GeoZarrProjFormat.CODE

    @classmethod
    def from_user_input(
        cls,
        value: str | int | dict[str, Any],
        *,
        crs_format: GeoZarrProjFormat = GeoZarrProjFormat.CODE,
    ) -> GeoZarrProj:
        """Build from any input accepted by :meth:`pyproj.CRS.from_user_input`."""
        return cls(crs=pyproj.CRS.from_user_input(value), crs_format=crs_format)

    def rio_input(self) -> str:
        """CRS string for :meth:`rioxarray.raster_array.RasterArray.write_crs`."""
        match self.crs_format:
            case GeoZarrProjFormat.CODE:
                authority = self.crs.to_authority()
                if authority is not None:
                    return f"{authority[0]}:{authority[1]}"
                return self.crs.to_wkt(version="WKT2_2019")
            case GeoZarrProjFormat.WKT2 | GeoZarrProjFormat.PROJJSON:
                return self.crs.to_wkt(version="WKT2_2019")

    def to_proj_attrs(self) -> dict[str, Any]:
        """Build ``proj:*`` attributes for this CRS."""
        match self.crs_format:
            case GeoZarrProjFormat.CODE:
                authority = self.crs.to_authority()
                if authority is not None:
                    return build_proj_attrs(crs_code=f"{authority[0]}:{authority[1]}")
                return build_proj_attrs(wkt2=self.crs.to_wkt(version="WKT2_2019"))
            case GeoZarrProjFormat.WKT2:
                return build_proj_attrs(wkt2=self.crs.to_wkt(version="WKT2_2019"))
            case GeoZarrProjFormat.PROJJSON:
                return build_proj_attrs(projjson=self.crs.to_json_dict())
