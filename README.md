# eodc-geozarr

GeoZarr convention attribute builders — an opinionated bridge between
[pyproj](https://pyproj4.github.io/pyproj/) and
[zarr-cm](https://github.com/zarr-conventions/zarr-cm).

It produces the plain attribute dicts that make up the `attributes` block of a
Zarr v3 group or array for the GeoZarr conventions `proj:`, `spatial:` and
`multiscales`, plus an interim `dggs:` placeholder.

Extracted from `cube-factory` so that datacube products can write GeoZarr
metadata without depending on the whole Icechunk/dask/cubed stack.

```bash
uv add "eodc-geozarr @ git+https://github.com/eodcgmbh/eodc-geozarr.git@main"
```

## Scope

`zarr_cm` owns the conventions themselves: schemas, validation, revisions, and
the `zarr_conventions` registry entries. This package adds only what it
deliberately does not:

- **A pyproj bridge.** `GeoZarrProj` holds a canonical `pyproj.CRS` and decides
  how to serialise it — authority code when one exists, WKT2 otherwise — and
  hands rioxarray a matching CRS string via `rio_input()`.
- **Domain defaults for gridded data.** `GeoZarrSpatial` defaults to `("y", "x")`
  dims and `"pixel"` registration, and infers `transform_type="affine"`.
- **Layout rules the schema does not encode**, e.g. `derived_from` requires a
  `transform`.
- **`geozarr_attrs`**, which emits several conventions at once together with a
  matching `zarr_conventions` registry array, so the registry always describes
  exactly the conventions present.

Everything returned is a plain `dict`, never a model, so it merges straight into
`xarray.Dataset.attrs`.

## Usage

```python
import eodc_geozarr as gz

crs = gz.GeoZarrProj.from_user_input("EPSG:27704")  # Equi7Grid EU
spatial = gz.GeoZarrSpatial(
    transform=(10.0, 0.0, 5400000.0, 0.0, -10.0, 2700000.0),
    shape=(10000, 10000),
)

attrs = gz.geozarr_attrs(crs=crs, spatial=spatial)
# {"proj:code": "EPSG:27704", "spatial:transform": [...], "zarr_conventions": [...]}

group.attrs.update(attrs)  # or ds.attrs.update(attrs)
```

Add a pyramid by passing the layout, one entry per level:

```python
attrs = gz.geozarr_attrs(
    crs=crs,
    multiscales=[
        {"asset": "0"},
        {"asset": "1", "derived_from": "0", "transform": {"scale": [2.0, 2.0]}},
    ],
)
```

The individual builders (`build_proj_attrs`, `build_spatial_attrs`,
`build_multiscales_attrs`, `build_zarr_conventions`, `merge_attrs`) are public
too, for callers that want to assemble attrs themselves.
`build_zarr_conventions` accepts the legacy `"geo-proj"` spelling as an alias for
`"proj"`, since `zarr_cm.ConventionName` still carries it and so do stores
written before the upstream rename.

## Convention revisions

Each convention in `zarr_cm` ships at one or more numbered *revisions*. A
revision fixes the convention's JSON Schema: which attribute keys are legal, how
strictly they are validated, and the `schema_url` written into the store's
`zarr_conventions` array.

This package writes at whatever revision the installed `zarr_cm` declares
latest, rather than pinning one — a pin nobody updates goes stale, and every
store records the revision that wrote it in its own `schema_url`, so drift stays
auditable after the fact. Reading is unaffected either way:
`zarr_cm.<convention>.detect()` sniffs the revision from the store.

`current_revisions()` reports what is in use:

| Convention | Current | Notes |
|---|---|---|
| `proj:` | `r3` | r2 restricted `proj:code` to `^[A-Z]+:[0-9]+$`, so `OGC:CRS84` was invalid |
| `spatial:` | `r3` | same keys as r2, looser validation |
| `multiscales` | `r2` | the only revision published so far |

`tests/test_conventions.py` asserts these, so a `zarr_cm` upgrade that ships a
new revision surfaces as one failing test rather than silently changing what gets
written. When it fails: read what changed, confirm the new attributes are what
you want, update `EXPECTED_REVISIONS`. Stricter validation would fail loudly at
ingest anyway; the test is there for the revisions that change quietly.

## Not in this package

- **`cf_time_attrs`** — CF, not GeoZarr. It stays in cube-factory.
- **`combine_geozarr_attrs`** — dropped in the extraction; it had no callers, and
  `zarr_cm.create_many` already does the job.

## Renames from `cube_factory._geozarr`

The convention was renamed `geo-proj` → `proj` upstream; this package follows it.

| Old | New |
|---|---|
| `build_geo_proj_attrs` | `build_proj_attrs` |
| `GeoZarrProj.to_geo_proj_attrs` | `GeoZarrProj.to_proj_attrs` |
| `GEO_PROJ_UUID` | `PROJ_UUID` |

Everything else keeps its name. Emitted attributes are unchanged — verified
identical across 66 builder cases and 11 `ZarrGroup` / `ZarrMultiscaleGroup`
configurations, including the `zarr_conventions` registry entries.

## Known issues

- Writing a CRS onto a group with no y/x spatial dims (e.g. HEALPix) produces a
  bogus identity `GeoTransform`. Carried over from cube-factory
  (`ZarrGroup.to_dataset` in `_core.py`); the fix belongs wherever the
  rioxarray-facing write path ends up living.

## Development

```bash
uv sync --all-groups
just test        # pytest
just check       # ruff lint + format + ty
```
