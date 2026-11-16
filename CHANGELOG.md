# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->

## [0.2.0](https://github.com/eodcgmbh/zarr-cm-tree/releases/tag/v0.2.0) - 2026-11-16

### Changed

- **BREAKING:** `GeoZarrSpatial` is keyword-only; `transform` is optional (default `None`), so dims-only `spatial:` attrs are possible.
- `build_spatial_attrs` raises `ValueError` for `transform_type="affine"` without `transform`.


## [0.1.0](https://github.com/eodcgmbh/zarr-cm-tree/releases/tag/0.1.0) - 2026-08-06

### Summary

- initial version
