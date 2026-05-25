import sys

from django.apps import AppConfig


class DataappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dataapp"
    verbose_name = "Carbon Data Review"

    def ready(self):
        if len(sys.argv) < 2 or sys.argv[1] not in ("runserver", "shell", "shell_plus", "uwsgi", "gunicorn"):
            return

        try:
            from django.db.utils import OperationalError
            from .models import Tenant, ImportBatch, EmissionRecord
        except OperationalError:
            return
        except Exception:
            return

        if Tenant.objects.count() == 0:
            Tenant.objects.create(name="ACME Corporation", slug="acme-corp")

        tenant = Tenant.objects.filter(slug="acme-corp").first()
        if not tenant or EmissionRecord.objects.exists():
            return

        sample_records = [
            {
                "source_type": "sap",
                "source_name": "SAP Fuel & Procurement",
                "original_filename": "sample-sap.csv",
                "row_count": 1,
                "source_raw": {"fuel_type": "diesel"},
                "source_row_id": "sap-001",
                "observation_date": "2026-05-01",
                "category": "Diesel fuel",
                "scope": "scope_1",
                "commodity": "Diesel",
                "location_code": "US01",
                "supplier": "ACME Fuel Partners",
                "quantity_value": 1200.0,
                "quantity_unit": "L",
                "normalized_quantity": 1200.0,
                "normalized_unit": "L",
                "emission_kg_co2e": 3288.0,
                "cost_usd": 1420.50,
                "description": "Onsite diesel consumption",
                "flagged_reasons": ["High fuel consumption"],
            },
            {
                "source_type": "utility",
                "source_name": "Utility Electricity",
                "original_filename": "sample-utility.csv",
                "row_count": 1,
                "source_raw": {"utility_account": "ELEC-US-01"},
                "source_row_id": "util-001",
                "observation_date": "2026-04-30",
                "category": "Electricity",
                "scope": "scope_2",
                "commodity": "Grid electricity",
                "location_code": "US01",
                "supplier": "Local Utility Co.",
                "quantity_value": 8500.0,
                "quantity_unit": "kWh",
                "normalized_quantity": 8500.0,
                "normalized_unit": "kWh",
                "emission_kg_co2e": 3575.0,
                "cost_usd": 1020.00,
                "description": "Office building electricity use",
                "flagged_reasons": [],
            },
            {
                "source_type": "travel",
                "source_name": "Corporate Travel",
                "original_filename": "sample-travel.csv",
                "row_count": 1,
                "source_raw": {"trip_type": "air"},
                "source_row_id": "travel-001",
                "observation_date": "2026-05-10",
                "category": "Air travel",
                "scope": "scope_3",
                "commodity": "Flight miles",
                "location_code": "US03",
                "supplier": "Acme Airlines",
                "quantity_value": 12000.0,
                "quantity_unit": "miles",
                "normalized_quantity": 12000.0,
                "normalized_unit": "mi",
                "emission_kg_co2e": 4680.0,
                "cost_usd": 3400.00,
                "description": "Employee flight for customer visit",
                "flagged_reasons": ["International travel"],
            },
        ]

        for sample in sample_records:
            batch = ImportBatch.objects.create(
                tenant=tenant,
                source_name=sample["source_name"],
                source_type=sample["source_type"],
                original_filename=sample["original_filename"],
                row_count=sample["row_count"],
                source_details={"seeded": True},
            )
            EmissionRecord.objects.create(
                tenant=tenant,
                batch=batch,
                source_type=batch.source_type,
                source_name=batch.source_name,
                source_row_id=sample["source_row_id"],
                source_raw=sample["source_raw"],
                observation_date=sample["observation_date"],
                category=sample["category"],
                scope=sample["scope"],
                commodity=sample["commodity"],
                location_code=sample["location_code"],
                supplier=sample["supplier"],
                quantity_value=sample["quantity_value"],
                quantity_unit=sample["quantity_unit"],
                normalized_quantity=sample["normalized_quantity"],
                normalized_unit=sample["normalized_unit"],
                emission_kg_co2e=sample["emission_kg_co2e"],
                cost_usd=sample["cost_usd"],
                description=sample["description"],
                flagged_reasons=sample["flagged_reasons"],
            )
