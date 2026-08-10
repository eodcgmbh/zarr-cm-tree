"""Tests for the ``multiscales`` layout builders."""

from __future__ import annotations

import pytest

from zarr_cm_tree import build_multiscales_attrs


class TestBuildMultiscalesAttrs:
    def test_level0_only(self):
        attrs = build_multiscales_attrs([{"asset": "0"}])
        assert attrs == {"multiscales": {"layout": [{"asset": "0"}]}}

    def test_two_levels_with_derived(self):
        attrs = build_multiscales_attrs(
            [
                {"asset": "0"},
                {
                    "asset": "1",
                    "derived_from": "0",
                    "transform": {"scale": [2.0, 2.0]},
                    "resampling_method": "mean",
                },
            ],
            resampling_method="mean",
        )
        ms = attrs["multiscales"]
        assert ms["resampling_method"] == "mean"
        assert ms["layout"][1]["derived_from"] == "0"
        assert ms["layout"][1]["transform"] == {"scale": [2.0, 2.0]}
        assert ms["layout"][1]["resampling_method"] == "mean"

    def test_no_zarr_conventions_entry(self):
        # The registry entry is added separately by build_zarr_conventions.
        assert "zarr_conventions" not in build_multiscales_attrs([{"asset": "0"}])

    def test_empty_layout_raises(self):
        with pytest.raises(ValueError, match="at least one level"):
            build_multiscales_attrs([])

    def test_missing_asset_raises(self):
        with pytest.raises(ValueError, match="'asset'"):
            build_multiscales_attrs([{"derived_from": "0"}])

    def test_derived_from_without_transform_raises(self):
        with pytest.raises(ValueError, match="'derived_from' but no 'transform'"):
            build_multiscales_attrs(
                [{"asset": "0"}, {"asset": "1", "derived_from": "0"}]
            )

    def test_input_is_not_mutated(self):
        layout = [{"asset": "0"}]
        build_multiscales_attrs(layout)
        assert layout == [{"asset": "0"}]
