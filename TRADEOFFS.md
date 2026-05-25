# TRADEOFFS

## 1. No direct PDF bill ingestion

I did not build PDF parsing or OCR for utility bills.
- Why: PDF ingestion is a substantial project by itself and not necessary for an MVP that proves the normalization and review flow.
- Tradeoff: the prototype is limited to CSV-based portal exports.

## 2. No authenticated SAP/API connectors

I did not build a live SAP connector or Concur/Navan API integration.
- Why: establishing enterprise API credentials, OAuth flows, and secured connectors is orthogonal to the core data-model and review workflow.
- Tradeoff: the current prototype requires export files rather than live system sync.

## 3. No full flight distance or hotel factor engine

I used simple fixed emission factors for flights, hotels, and ground transport.
- Why: building a complete factor registry and distance resolver would take more than the prototype window.
- Tradeoff: the system demonstrates category-specific normalization, but it is not a production-grade emissions calculator.
