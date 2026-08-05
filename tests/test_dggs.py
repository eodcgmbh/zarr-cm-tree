"""Tests for the interim ``dggs:`` builders."""

from __future__ import annotations

from eodc_geozarr import DGGS_NAMESPACE, build_dggs_attrs


class TestBuildDggsAttrs:
    def test_healpix(self):
        attrs = build_dggs_attrs("healpix", level=10, indexing_scheme="nested")
        assert attrs == {
            "dggs:grid_name": "healpix",
            "dggs:level": 10,
            "dggs:indexing_scheme": "nested",
        }

    def test_level_is_a_plain_int(self):
        # numpy integers are not JSON-serialisable as Zarr attributes.
        level = build_dggs_attrs("healpix", level=10, indexing_scheme="nested")
        assert type(level["dggs:level"]) is int

    def test_all_keys_namespaced(self):
        attrs = build_dggs_attrs("healpix", level=1, indexing_scheme="ring")
        assert all(key.startswith(DGGS_NAMESPACE) for key in attrs)
