"""Tests for the ``spatial:`` builders."""

from __future__ import annotations

import pytest

from zarr_cm_tree import GeoZarrSpatial, build_spatial_attrs


class TestGeoZarrSpatial:
    def test_full(self):
        spatial = GeoZarrSpatial(
            transform=(10.0, 0.0, 100.0, 0.0, -10.0, 200.0),
            shape=(4, 5),
            bbox=(100.0, 160.0, 150.0, 200.0),
            registration="node",
        )
        attrs = spatial.to_attrs()
        assert attrs["spatial:transform"] == [10.0, 0.0, 100.0, 0.0, -10.0, 200.0]
        assert attrs["spatial:transform_type"] == "affine"
        assert attrs["spatial:shape"] == [4, 5]
        assert attrs["spatial:bbox"] == [100.0, 160.0, 150.0, 200.0]
        assert attrs["spatial:registration"] == "node"

    def test_defaults(self):
        attrs = GeoZarrSpatial(transform=(10.0, 0.0, 0.0, 0.0, -10.0, 0.0)).to_attrs()
        assert attrs["spatial:dimensions"] == ["y", "x"]
        assert attrs["spatial:registration"] == "pixel"

    def test_custom_dims(self):
        # ERA5-Land passes its own lat/lon labels rather than y/x.
        spatial = GeoZarrSpatial(
            transform=(0.1, 0.0, -180.0, 0.0, -0.1, 90.0),
            dims=("latitude", "longitude"),
        )
        assert spatial.to_attrs()["spatial:dimensions"] == ["latitude", "longitude"]


class TestBuildSpatialAttrs:
    def test_minimal_dimensions_only(self):
        attrs = build_spatial_attrs(["y", "x"])
        assert attrs["spatial:dimensions"] == ["y", "x"]
        assert attrs["spatial:registration"] == "pixel"
        assert "spatial:transform" not in attrs

    def test_full(self):
        attrs = build_spatial_attrs(
            ["y", "x"],
            transform=(10.0, 0.0, 100.0, 0.0, -10.0, 200.0),
            shape=(4, 5),
            bbox=(100.0, 160.0, 150.0, 200.0),
            registration="node",
        )
        assert attrs["spatial:transform"] == [10.0, 0.0, 100.0, 0.0, -10.0, 200.0]
        assert attrs["spatial:transform_type"] == "affine"
        assert attrs["spatial:shape"] == [4, 5]
        assert attrs["spatial:bbox"] == [100.0, 160.0, 150.0, 200.0]
        assert attrs["spatial:registration"] == "node"

    def test_explicit_transform_type_is_kept(self):
        attrs = build_spatial_attrs(
            ["y", "x"],
            transform=(10.0, 0.0, 0.0, 0.0, -10.0, 0.0),
            transform_type="custom",
        )
        assert attrs["spatial:transform_type"] == "custom"

    def test_no_transform_type_without_transform(self):
        assert "spatial:transform_type" not in build_spatial_attrs(["y", "x"])

    def test_empty_dimensions_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            build_spatial_attrs([])
