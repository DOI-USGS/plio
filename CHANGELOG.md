# Changelog

All changes that impact users of this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!---
This document is intended for users of the applications and API. Changes to things
like tests should not be noted in this document.

When updating this file for a PR, add an entry for your change under Unreleased
and one of the following headings:
 - Added - for new features.
 - Changed - for changes in existing functionality.
 - Deprecated - for soon-to-be removed features.
 - Removed - for now removed features.
 - Fixed - for any bug fixes.
 - Security - in case of vulnerabilities.

If the heading does not yet exist under Unreleased, then add it as a 3rd heading,
with three #.


When preparing for a public release candidate add a new 2nd heading, with two #, under
Unreleased with the version number and the release date, in year-month-day
format. Then, add a link for the new version at the bottom of this document and
update the Unreleased link so that it compares against the latest release tag.


When preparing for a bug fix release create a new 2nd heading above the Fixed
heading to indicate that only the bug fixes and security fixes are in the bug fix
release.
-->

## [Unreleased]
### Fixed
- Fixed a bug in which prefixes and suffixes were not properly prepended/appended to point_id [#213](https://github.com/DOI-USGS/plio/issues/213)
- Fixed a deprecation warning by changing to importlib tools for version determination [#218](https://github.com/DOI-USGS/plio/issues/218)

# [1.6.0]()

### Added
- Hard coded support for `csminit`ed cubes that have serial numbers that differ from `spiceinit`ed cubes.
- Added support for scale and offset for GeoDataset objects.

### Fixed
- Fixed a bug where scale and offset were being applied backwards to GeoDataset objects.
- Copied and pieced together .proto files from ISIS3/src/control/objs/ControlNetVersioner to plio/plio/io.
  Regenerated _pb2.py files with protoc 28.2 to fix error with old-protoc-generated files. [#210](https://github.com/DOI-USGS/plio/issues/210)

## [1.5.5]()
### Fixed
- Fixed a bug in which read_ipf_str() returned a ValueError [#200](https://github.com/DOI-USGS/plio/issues/200)

## [1.5.4]()
### Fixed
- Tests for gdal > 3 and pvl > 1.0. This includes fixing the `k` value on the MOLA polar stereographic test data and updating the proj string for GDAL > 3 (new fields are included).
- Conditional GDAL import to support gdal > 3.0
- `generate_isis_serial` to work on cubes that have been run through `jigsaw` by removing the custom `SerialNumberDecoder`. Fixes [#194](https://github.com/DOI-USGS/plio/issues/194)
- Updated `create_pvl_header()` to add a newline (`\n`) character to the end of the pvl string. This ensures that the control networks can be written, then read back in using pvl 1.3.0 [#193](https://github.com/USGS-Astrogeology/plio/pull/193)

## [1.5.3]()
### Fixed
- Updated `read_gpf()` to correctly parse hybrid-style GPFs from Socet GXP. [#191](https://github.com/USGS-Astrogeology/plio/pull/191)

## [1.5.2]() 

- Made gdal an optional dependency. [#186](https://github.com/USGS-Astrogeology/plio/pull/186)

## [1.5.1]()

### Fixed
- Updated documentation string for `compute_covariance`. [#177](https://github.com/USGS-Astrogeology/plio/pull/177)
- Improved performance of `to_isis`. [#181](https://github.com/USGS-Astrogeology/plio/issues/181)

## [1.5.0]()

### Added
- Added this CHANGELOG.md file to track changes to the library
- Added a warning when to_isis is called without a target name fixing [#126](https://github.com/USGS-Astrogeology/plio/issues/126).
