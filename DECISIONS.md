# DECISIONS

## Source ingestion choices

- **SAP**: I chose a CSV-based SAP export model rather than IDoc/BAPI/OData.
  - Justification: enterprise onboarding often begins with file exchange and CSV exports are easier to prototype without live SAP credentials.
  - The parser accepts mixed English/German headers, inconsistent date formats, and fuel units like liters and gallons.

- **Utility electricity**: I chose a utility portal CSV export.
  - Justification: many facilities teams export meter bills as CSV before they have a direct API integration.
  - The model explicitly supports non-calendar billing periods and meter IDs.

- **Corporate travel**: I chose a travel expense export CSV similar to Concur/Navan.
  - Justification: these platforms commonly provide download exports for flights, hotels, and ground transport.
  - The model handles expense categories, airport codes, distances, and flags missing data.

## Ingestion mechanism

- I used file upload forms for all three sources.
- This is realistic for an onboarding prototype because actual enterprise data often arrives as exports rather than API credentials.
- It also keeps the prototype self-contained and easier to deploy.

## What subset is handled

- SAP: fuel usage and procurement rows with a CO2 factor field.
  - Ignored: full material master lookups, multi-leg BOM cost allocations, SAP IDoc structure, OData service metadata, vendor master enrichment.
- Utility: electricity bills with meter usage and cost.
  - Ignored: demand charges, time-of-use sub-meter splits, PDF bill extraction, tariff schedule rules.
- Travel: flight/hotel/ground expense rows.
  - Ignored: multi-leg itinerary reconstruction, currency conversion, passenger class, travel policy rules.

## What I would ask the PM

- Do you want a saved tenant onboarding profile so the same source mapping can be reused across months?
- Should the system preserve both raw source files and parsed batches in object storage?
- Do auditors need downloadable CSV/Excel exports of approved records?
