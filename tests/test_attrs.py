"""Tests for combining conventions into a single attrs dict."""

from __future__ import annotations

import pytest

from eodc_geozarr import (
    MULTISCALES_UUID,
    PROJ_UUID,
    SPATIAL_UUID,
    GeoZarrProj,
    GeoZarrSpatial,
    geozarr_attrs,
)

CRS = GeoZarrProj.from_user_input("EPSG:27704")
SPATIAL = GeoZarrSpatial(
    transform=(10.0, 0.0, 5400000.0, 0.0, -10.0, 2700000.0),
    shape=(1000, 1000),
)
LAYOUT = [
    {"asset": "0"},
    {"asset": "1", "derived_from": "0", "transform": {"scale": [2.0, 2.0]}},
]


def uuids(attrs):
    return [entry["uuid"] for entry in attrs["zarr_conventions"]]


class TestGeozarrAttrs:
    def test_empty_without_conventions(self):
        assert geozarr_attrs() == {}

    def test_crs_only(self):
        attrs = geozarr_attrs(crs=CRS)
        assert attrs["proj:code"] == "EPSG:27704"
        assert uuids(attrs) == [PROJ_UUID]

    def test_spatial_only(self):
        attrs = geozarr_attrs(spatial=SPATIAL)
        assert attrs["spatial:transform_type"] == "affine"
        assert uuids(attrs) == [SPATIAL_UUID]

    def test_multiscales_only(self):
        attrs = geozarr_attrs(multiscales=LAYOUT)
        assert attrs["multiscales"]["layout"][1]["derived_from"] == "0"
        assert uuids(attrs) == [MULTISCALES_UUID]

    def test_registry_order_is_fixed(self):
        attrs = geozarr_attrs(crs=CRS, spatial=SPATIAL, multiscales=LAYOUT)
        assert uuids(attrs) == [PROJ_UUID, SPATIAL_UUID, MULTISCALES_UUID]

    def test_registry_describes_only_active_conventions(self):
        assert uuids(geozarr_attrs(crs=CRS, multiscales=LAYOUT)) == [
            PROJ_UUID,
            MULTISCALES_UUID,
        ]

    def test_empty_multiscales_treated_as_absent(self):
        # Matches cube-factory, where a group with no named children emits no
        # multiscales block rather than raising.
        assert geozarr_attrs(crs=CRS, multiscales=[]) == geozarr_attrs(crs=CRS)

    def test_resampling_method_forwarded(self):
        attrs = geozarr_attrs(multiscales=LAYOUT, resampling_method="mean")
        assert attrs["multiscales"]["resampling_method"] == "mean"

    def test_all_keys_present_together(self):
        attrs = geozarr_attrs(crs=CRS, spatial=SPATIAL, multiscales=LAYOUT)
        assert {"proj:code", "spatial:transform", "multiscales"} <= set(attrs)

    def test_invalid_layout_still_raises(self):
        with pytest.raises(ValueError, match="'asset'"):
            geozarr_attrs(crs=CRS, multiscales=[{"derived_from": "0"}])
