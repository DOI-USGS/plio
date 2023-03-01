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
- Updated `create_pvl_header()` at add a newline (`\n`) character to the end of the pvl string. This ensures that the controls networks can be read in pvl 1.3.0 [#193](https://github.com/USGS-Astrogeology/plio/pull/193)

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
