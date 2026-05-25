import csv
import io
from datetime import datetime

SAP_HEADER_MAP = {
    "document number": "document_number",
    "belegnummer": "document_number",
    "posting date": "posting_date",
    "buchungsdatum": "posting_date",
    "plant": "plant",
    "werk": "plant",
    "material": "material",
    "short text": "short_text",
    "kurztext": "short_text",
    "quantity": "quantity",
    "menge": "quantity",
    "unit": "unit",
    "me": "unit",
    "vendor": "vendor",
    "lieferant": "vendor",
    "co2 factor kg/unit": "co2_factor",
    "co2-faktor kg/me": "co2_factor",
    "emission": "emission_kg_co2e",
    "emissions": "emission_kg_co2e",
    "emission kg co2e": "emission_kg_co2e",
    "amount": "amount",
    "betrag": "amount",
}

UTILITY_HEADER_MAP = {
    "meter id": "meter_id",
    "service address": "service_address",
    "bill start date": "bill_start",
    "start date": "bill_start",
    "bill end date": "bill_end",
    "end date": "bill_end",
    "usage (kwh)": "usage_kwh",
    "energy usage kwh": "usage_kwh",
    "usage": "usage_kwh",
    "amount": "amount",
    "total cost": "amount",
    "rate class": "rate_class",
    "billing period": "billing_period",
}

TRAVEL_HEADER_MAP = {
    "expense type": "expense_type",
    "category": "expense_type",
    "trip type": "expense_type",
    "trip start date": "start_date",
    "departure date": "start_date",
    "trip end date": "end_date",
    "arrival date": "end_date",
    "origin": "origin",
    "destination": "destination",
    "distance (mi)": "distance_miles",
    "distance miles": "distance_miles",
    "distance": "distance_miles",
    "amount": "amount",
    "currency": "currency",
    "traveler": "traveler",
}

UNIT_NORMALIZATION = {
    "l": ("liters", 1.0),
    "liters": ("liters", 1.0),
    "liter": ("liters", 1.0),
    "gal": ("liters", 3.78541),
    "gallon": ("liters", 3.78541),
    "kg": ("kg", 1.0),
    "kwh": ("kwh", 1.0),
    "miles": ("miles", 1.0),
    "mi": ("miles", 1.0),
    "mile": ("miles", 1.0),
    "nights": ("nights", 1.0),
}

def normalize_headers(row, mapping):
    normalized = {}
    for raw_name, value in row.items():
        if raw_name is None:
            continue
        key = raw_name.strip().lower()
        normalized[mapping.get(key, key)] = value.strip() if isinstance(value, str) else value
    return normalized


def parse_date(value):
    if not value:
        return None
    for fmt in ["%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y", "%Y/%m/%d"]:
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except Exception:
            continue
    return None


def parse_float(value):
    if value is None:
        return None
    text = str(value).replace("\u00a0", "").replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


def normalize_unit(unit):
    if not unit:
        return None, None
    key = str(unit).strip().lower()
    return UNIT_NORMALIZATION.get(key, (key, 1.0))


def parse_sap_rows(file_obj):
    text = io.TextIOWrapper(file_obj, encoding="utf-8", errors="replace")
    reader = csv.DictReader(text)
    rows = []
    for raw in reader:
        normalized = normalize_headers(raw, SAP_HEADER_MAP)
        quantity = parse_float(normalized.get("quantity"))
        unit, factor = normalize_unit(normalized.get("unit"))
        normalized_quantity = quantity * factor if quantity is not None else None
        co2_factor = parse_float(normalized.get("co2_factor"))
        emission = normalized_quantity * co2_factor if normalized_quantity is not None and co2_factor is not None else None
        category = "Fuel" if "fuel" in str(normalized.get("material", "")).lower() or "diesel" in str(normalized.get("short_text", "")).lower() else "Procurement"
        scope = "scope_1" if category == "Fuel" else "scope_3"
        row_id = normalized.get("document_number") or normalized.get("posting_date")
        flagged = []
        if quantity is None or unit is None:
            flagged.append("missing quantity or unit")
        if category == "Procurement" and co2_factor is None and parse_float(normalized.get("emission_kg_co2e")) is None:
            flagged.append("missing procurement emission factor")
        if parse_date(normalized.get("posting_date")) is None:
            flagged.append("unparseable date")

        explicit_emission = parse_float(normalized.get("emission_kg_co2e"))
        if emission is None and explicit_emission is not None:
            emission = explicit_emission

        rows.append({
            "source_row_id": str(row_id or "")[:255],
            "source_raw": normalized,
            "observation_date": parse_date(normalized.get("posting_date")),
            "category": category,
            "scope": scope,
            "commodity": normalized.get("material", ""),
            "location_code": normalized.get("plant", ""),
            "supplier": normalized.get("vendor", ""),
            "quantity_value": quantity,
            "quantity_unit": unit or normalized.get("unit", ""),
            "normalized_quantity": normalized_quantity,
            "normalized_unit": unit,
            "emission_kg_co2e": emission,
            "cost_usd": parse_float(normalized.get("amount")),
            "description": normalized.get("short_text", ""),
            "flagged_reasons": flagged,
        })
    return rows


def parse_utility_rows(file_obj):
    text = io.TextIOWrapper(file_obj, encoding="utf-8", errors="replace")
    reader = csv.DictReader(text)
    rows = []
    for raw in reader:
        normalized = normalize_headers(raw, UTILITY_HEADER_MAP)
        usage = parse_float(normalized.get("usage_kwh"))
        start = parse_date(normalized.get("bill_start"))
        end = parse_date(normalized.get("bill_end"))
        flagged = []
        if usage is None:
            flagged.append("missing consumption")
        if start is None or end is None:
            flagged.append("missing billing period")
        if start and end and (end - start).days not in (28, 29, 30, 31):
            flagged.append("non-calendar billing period")
        rows.append({
            "source_row_id": str(normalized.get("meter_id", ""))[:255],
            "source_raw": normalized,
            "observation_date": start,
            "category": "Electricity",
            "scope": "scope_2",
            "commodity": "Electricity",
            "location_code": normalized.get("service_address", ""),
            "supplier": normalized.get("rate_class", ""),
            "quantity_value": usage,
            "quantity_unit": "kwh",
            "normalized_quantity": usage,
            "normalized_unit": "kwh",
            "emission_kg_co2e": usage * 0.41 if usage is not None else None,
            "cost_usd": parse_float(normalized.get("amount")),
            "description": f"Meter {normalized.get('meter_id', '')} bill {start} to {end}",
            "flagged_reasons": flagged,
        })
    return rows


def parse_travel_rows(file_obj):
    text = io.TextIOWrapper(file_obj, encoding="utf-8", errors="replace")
    reader = csv.DictReader(text)
    rows = []
    for raw in reader:
        normalized = normalize_headers(raw, TRAVEL_HEADER_MAP)
        expense_type = str(normalized.get("expense_type", "")).lower()
        start = parse_date(normalized.get("start_date"))
        end = parse_date(normalized.get("end_date"))
        distance = parse_float(normalized.get("distance_miles"))
        amount = parse_float(normalized.get("amount"))
        category = "Unknown"
        normalized_quantity = None
        normalized_unit = ""
        emission = None
        flagged = []
        if "flight" in expense_type or "air" in expense_type:
            category = "Flight"
            normalized_quantity = distance
            normalized_unit = "miles"
            emission = distance * 0.2 if distance is not None else None
        elif "hotel" in expense_type or "lodging" in expense_type:
            category = "Hotel"
            nights = None
            if start and end:
                nights = max(1, (end - start).days)
            normalized_quantity = nights
            normalized_unit = "nights"
            emission = nights * 15 if nights is not None else None
        elif "taxi" in expense_type or "ride" in expense_type or "ground" in expense_type:
            category = "Ground Transport"
            normalized_quantity = distance
            normalized_unit = "miles"
            emission = distance * 0.18 if distance is not None else None
        else:
            category = "Travel"
            if distance is not None:
                normalized_quantity = distance
                normalized_unit = "miles"
                emission = distance * 0.18
        if category == "Flight" and distance is None:
            flagged.append("missing flight distance")
        if category == "Unknown":
            flagged.append("unrecognized travel category")
        rows.append({
            "source_row_id": str(normalized.get("origin", ""))[:255],
            "source_raw": normalized,
            "observation_date": start,
            "category": category,
            "scope": "scope_3",
            "commodity": expense_type.title(),
            "location_code": f"{normalized.get('origin', '')}->{normalized.get('destination', '')}",
            "supplier": normalized.get("traveler", ""),
            "quantity_value": distance,
            "quantity_unit": "miles" if distance is not None else "",
            "normalized_quantity": normalized_quantity,
            "normalized_unit": normalized_unit,
            "emission_kg_co2e": emission,
            "cost_usd": amount,
            "description": f"{expense_type.title()} trip {normalized.get('origin', '')}->{normalized.get('destination', '')}",
            "flagged_reasons": flagged,
        })
    return rows
