# SOURCES

## SAP fuel and procurement

### Real-world format researched
- Typical SAP export is a flat CSV from SAP GUI reports or SAP Query (transaction MB51, ME2N, or custom Z-report).
- Exports often contain German headers like `Buchungsdatum`, `Werk`, `Menge`, `ME`.
- Unit data can be inconsistent: liters, gallons, kilograms.

### What I learned
- Real SAP exports are noisy: header variants, date formats, inconsistent units, and plant codes that require lookup tables.
- Fuel rows usually have a material type or short text containing `Diesel`, `Gas`, `Fuel`.

### Sample data shape
- `Document Number`, `Posting Date`, `Plant`, `Material`, `Short Text`, `Quantity`, `Unit`, `Vendor`, `CO2-Factor kg/ME`, `Amount`
- Example: `45000123,2025-02-14,PL01,Diesel A,Fuel diesel delivery,1200,Liter,SAP Fuel Co,2.68,1800`

### What would break in real deployment
- If the export uses a true SAP IDoc structure or XML instead of CSV.
- If CO2 factor is not provided and there is no factor lookup table.
- If plant codes need mapping to real facility metadata.

## Utility electricity

### Real-world format researched
- Utilities often provide meter bill exports as CSV with columns for `Meter ID`, `Bill Start Date`, `Bill End Date`, `Usage (kWh)`, and `Amount`.
- Billing periods frequently do not align to calendar months.

### What I learned
- Billing periods are the key real-world complexity: facilities often pay one bill for 28–35 days.
- Tariff structure matters, but can be simplified for proof of concept.

### Sample data shape
- `Meter ID`, `Service Address`, `Bill Start Date`, `Bill End Date`, `Usage (kWh)`, `Amount`, `Rate Class`
- Example: `EL-1001,Plant 1,2025-03-02,2025-04-01,11250,1520,Commercial`

### What would break in real deployment
- If the customer only has PDF bills, not CSV exports.
- If the utility bill includes multiple submeter lines or demand charges.
- If the bill uses a different energy unit like therms or MWh.

## Corporate travel

### Real-world format researched
- Concur, Navan, and similar platforms expose expense/export CSVs with expense type, travel dates, origin/destination, distance, and amount.
- Distances are sometimes absent; airports are often the only location information.

### What I learned
- The export may provide `Expense Type` values such as `Flight`, `Hotel`, `Ground Transport`.
- When distances are missing, a realistic system would need an airport-to-airport distance resolver.

### Sample data shape
- `Expense Type`, `Trip Start Date`, `Trip End Date`, `Origin`, `Destination`, `Distance (mi)`, `Amount`, `Currency`, `Traveler`
- Example: `Flight,2025-03-10,2025-03-10,JFK,LAX,2475,870,USD,Alice Johnson`

### What would break in real deployment
- If the travel export uses separate itinerary and expense records.
- If the platform exports multi-leg flights without a consolidated distance.
- If expenses are in multiple currencies and currency conversion is required.
