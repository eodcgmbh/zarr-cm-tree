"""Tests for the ``proj:`` builders and the pyproj bridge."""

from __future__ import annotations

import pyproj

from eodc_geozarr import GeoZarrProj, GeoZarrProjFormat, build_proj_attrs


class TestBuildProjAttrs:
    def test_none_returns_empty(self):
        assert build_proj_attrs() == {}

    def test_epsg_code(self):
        assert build_proj_attrs(crs_code="EPSG:32633") == {"proj:code": "EPSG:32633"}

    def test_ogc_crs84(self):
        assert build_proj_attrs(crs_code="OGC:CRS84") == {"proj:code": "OGC:CRS84"}

    def test_wkt2(self):
        wkt = 'PROJCRS["WGS 84 / UTM zone 33N",BASEGEOGCRS["WGS 84",...]]'
        attrs = build_proj_attrs(wkt2=wkt)
        assert "proj:wkt2" in attrs
        assert attrs["proj:wkt2"] == wkt

    def test_projjson(self):
        projjson = pyproj.CRS.from_user_input("EPSG:32633").to_json_dict()
        assert build_proj_attrs(projjson=projjson) == {"proj:projjson": projjson}


class TestGeoZarrProj:
    def test_epsg_code_format(self):
        spec = GeoZarrProj.from_user_input("EPSG:32633")
        assert spec.crs_format is GeoZarrProjFormat.CODE
        assert spec.to_proj_attrs() == {"proj:code": "EPSG:32633"}

    def test_wkt2_format(self):
        crs = pyproj.CRS.from_user_input("EPSG:32633")
        wkt = crs.to_wkt(version="WKT2_2019")
        spec = GeoZarrProj(crs=crs, crs_format=GeoZarrProjFormat.WKT2)
        assert spec.to_proj_attrs() == {"proj:wkt2": wkt}

    def test_projjson_format(self):
        crs = pyproj.CRS.from_user_input("EPSG:32633")
        spec = GeoZarrProj(crs=crs, crs_format=GeoZarrProjFormat.PROJJSON)
        assert spec.to_proj_attrs() == {"proj:projjson": crs.to_json_dict()}

    def test_proj4_normalises_to_epsg(self):
        proj4 = "+proj=utm +zone=33 +datum=WGS84 +units=m +no_defs"
        spec = GeoZarrProj.from_user_input(proj4)
        assert spec.to_proj_attrs() == {"proj:code": "EPSG:32633"}

    def test_ogc_crs84(self):
        spec = GeoZarrProj.from_user_input("OGC:CRS84")
        assert spec.to_proj_attrs() == {"proj:code": "OGC:CRS84"}

    def test_equi7_subgrids(self):
        # The Equi7Grid codes the S2 product writes; EPSG:27704 is EU, 27707 SA.
        for code in ("EPSG:27704", "EPSG:27707"):
            assert GeoZarrProj.from_user_input(code).to_proj_attrs() == {
                "proj:code": code
            }

    def test_rio_input_uses_authority_code(self):
        assert GeoZarrProj.from_user_input("EPSG:32633").rio_input() == "EPSG:32633"

    def test_rio_input_falls_back_to_wkt2_without_authority(self):
        # A bare proj4 string with no authority match has no code to emit.
        crs = pyproj.CRS.from_user_input("+proj=laea +lat_0=12 +lon_0=34 +datum=WGS84")
        spec = GeoZarrProj(crs=crs)
        assert spec.crs.to_authority() is None
        assert spec.rio_input() == crs.to_wkt(version="WKT2_2019")
        assert spec.to_proj_attrs() == {"proj:wkt2": crs.to_wkt(version="WKT2_2019")}

    def test_rio_input_wkt2_format(self):
        crs = pyproj.CRS.from_user_input("EPSG:32633")
        spec = GeoZarrProj(crs=crs, crs_format=GeoZarrProjFormat.WKT2)
        assert spec.rio_input() == crs.to_wkt(version="WKT2_2019")

    def test_is_hashable_and_comparable(self):
        # ``frozen=True`` matters: pydantic ZarrGroup equality in cube-factory
        # compares these, and tests assert ``group.crs == GeoZarrProj(...)``.
        a = GeoZarrProj.from_user_input("EPSG:27704")
        b = GeoZarrProj.from_user_input("EPSG:27704")
        assert a == b
        assert len({a, b}) == 1
