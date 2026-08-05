"""Tests for the convention registry, revision pinning, and attr merging."""

from __future__ import annotations

import pytest
from zarr_cm import multiscales as zcm_multiscales
from zarr_cm import proj as zcm_proj
from zarr_cm import spatial as zcm_spatial

from eodc_geozarr import (
    MULTISCALES_UUID,
    PROJ_UUID,
    SPATIAL_UUID,
    build_proj_attrs,
    build_zarr_conventions,
    convention_metadata,
    current_revisions,
    merge_attrs,
)


class TestBuildZarrConventions:
    def test_known_names(self):
        entries = build_zarr_conventions("proj", "spatial", "multiscales")
        uuids = [e["uuid"] for e in entries]
        assert uuids == [PROJ_UUID, SPATIAL_UUID, MULTISCALES_UUID]

    def test_geo_proj_alias(self):
        # Stores written before the upstream geo-proj -> proj rename, and
        # zarr_cm's own ConventionName literal, still use the old spelling.
        assert build_zarr_conventions("geo-proj") == build_zarr_conventions("proj")

    def test_order_is_preserved(self):
        entries = build_zarr_conventions("spatial", "proj")
        assert [e["uuid"] for e in entries] == [SPATIAL_UUID, PROJ_UUID]

    def test_entries_are_copies(self):
        entry = build_zarr_conventions("proj")[0]
        entry["uuid"] = "mutated"
        assert build_zarr_conventions("proj")[0]["uuid"] == PROJ_UUID

    def test_unknown_name_raises(self):
        with pytest.raises(KeyError, match="unknown GeoZarr convention"):
            build_zarr_conventions("not-a-convention")


EXPECTED_REVISIONS = {"proj": "r3", "spatial": "r3", "multiscales": "r2"}


class TestRevisions:
    def test_revisions_are_as_expected(self):
        # This package follows zarr_cm's latest revision per convention rather
        # than pinning one.  When this fails, zarr_cm has shipped a new
        # revision: read its changes, confirm the new attributes are what you
        # want written, then update EXPECTED_REVISIONS.  Stores written earlier
        # keep their own schema_url, so old data stays readable either way.
        assert current_revisions() == EXPECTED_REVISIONS

    @pytest.mark.parametrize(
        ("name", "module"),
        [
            ("proj", zcm_proj),
            ("spatial", zcm_spatial),
            ("multiscales", zcm_multiscales),
        ],
    )
    def test_registry_entry_matches_the_revision_in_use(self, name, module):
        # The registry entry written to a store must describe the same revision
        # the attributes were built with.
        revision = current_revisions()[name]
        assert convention_metadata(name)["schema_url"] == (
            getattr(module, revision).SCHEMA_URL
        )

    def test_ogc_crs84_needs_proj_r3(self):
        # Why the revision in use is not academic: r2 constrained proj:code to
        # ^[A-Z]+:[0-9]+$, which rejects the CRS the ASCAT SSM product writes.
        assert build_proj_attrs(crs_code="OGC:CRS84") == {"proj:code": "OGC:CRS84"}
        with pytest.raises(ValueError, match="must match"):
            zcm_proj.create(code="OGC:CRS84", revision="r2")


class TestMergeAttrs:
    def test_later_overrides_earlier(self):
        merged = merge_attrs({"a": 1, "b": 2}, {"b": 3, "c": 4})
        assert merged == {"a": 1, "b": 3, "c": 4}

    def test_none_skipped(self):
        merged = merge_attrs(None, {"a": 1}, None, {"b": 2})
        assert merged == {"a": 1, "b": 2}

    def test_empty_dicts_skipped(self):
        assert merge_attrs({}, {"a": 1}, {}) == {"a": 1}

    def test_inputs_not_mutated(self):
        first = {"a": 1}
        merge_attrs(first, {"b": 2})
        assert first == {"a": 1}
