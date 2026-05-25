# Data Model

## Core Entities

- `Tenant`
  - Represents a client company or tenant.
  - Supports multi-tenancy by scoping every imported row and batch to a tenant.

- `ImportBatch`
  - Tracks each ingestion event.
  - Stores `source_type`, `source_name`, original filename, row count, upload timestamp, and metadata.
  - Provides source-of-truth context for every row created from that batch.

- `EmissionRecord`
  - The normalized row consumed by analysts and auditors.
  - Stores both raw source payload (`source_raw`) and normalized fields.
  - Tracks provenance: `source_type`, `source_name`, `source_row_id`, `batch`, and `imported_at`.
  - Maintains edit metadata via `last_modified_at` and `last_modified_by`.
  - Includes `status` for analyst review (`pending`, `approved`, `rejected`).
  - Stores `flagged_reasons` for suspicious or incomplete data.

- `AuditEvent`
  - Appends an audit entry each time a record is approved or rejected.
  - Captures actor, action, notes, and timestamp.

## Scope 1/2/3

The model encodes GHG categories with a strict `scope` choice field:

- `scope_1` for direct fuel combustion from SAP fuel imports.
- `scope_2` for electricity consumption from utility portal CSV exports.
- `scope_3` for business travel and travel-related procurement.

This makes review dashboards and downstream reporting explicit.

## Unit normalization

Each `EmissionRecord` preserves both source units and normalized values:

- `quantity_value` / `quantity_unit` store the original consumed quantity.
- `normalized_quantity` / `normalized_unit` store the normalized quantity used for emissions calculations.

Normalization is performed at ingestion with unit conversions such as gallons to liters and distance in miles.

## Source-of-truth tracking

The model keeps source provenance at two levels:

- `ImportBatch` records the original upload event and source metadata.
- `EmissionRecord` stores row-level provenance: original payload, row identifier, source system, and upload timestamp.

When a record is edited or approved, `last_modified_at` and `last_modified_by` retain the latest editor, and `AuditEvent` creates a tamper-evident trail.

## Why this model?

This design is intentionally narrow enough to support realistic enterprise onboarding without overbuilding:

- It supports multiple clients with one database.
- It preserves raw source content for audit review.
- It provides a clean normalized review object for analysts.
- It captures both the ingestion event and post-ingestion review actions.
