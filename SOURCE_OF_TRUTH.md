# Source-of-Truth Policy

The `main` repository contains the authoritative source for the Digital Resource Companion.

For V1.0, the governing hierarchy is:

**Current textbook structure → canonical companion resources → synchronized catalogues and bundles → Web Companion and printable companion → immutable release packages.**

## Canonical resources

Canonical editable and machine-readable resources are maintained in:

- `chapters/`
- `worked_examples/`
- `process/`
- `catalogs/`

## Synchronized distribution layers

The following directories are public distribution layers and should not become independent sources of truth:

- `docs/`
- `publications/`
- `bundles/`

When a canonical resource changes, affected catalogues, website pages, printable documents, and bundles must be synchronized before release.

## Stable identifiers

Resource IDs, case IDs, Python-module IDs, chapter numbers, figure numbers, and table numbers should be preserved wherever possible. Printed page numbers are not persistent identifiers and should not be used as the sole companion reference.

## Release control

A release is ready only when:

1. canonical resources are aligned with the current book
2. catalogues have been regenerated
3. website and bundle copies are synchronized
4. worked examples and computational resources pass validation
5. internal links and structured files have been checked
6. version references are consistent; and
7. release checksums have been regenerated.

Zenodo provides the immutable archival snapshot of a released version. GitHub remains the maintained source for subsequent development.
