from rest_framework import serializers
from .models import AuditEvent, EmissionRecord, ImportBatch, Tenant


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["id", "name", "slug"]


class ImportBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportBatch
        fields = ["id", "source_name", "source_type", "uploaded_at", "original_filename", "row_count", "source_details"]


class EmissionRecordSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer(read_only=True)
    batch = ImportBatchSerializer(read_only=True)

    class Meta:
        model = EmissionRecord
        fields = [
            "id",
            "tenant",
            "batch",
            "source_type",
            "source_name",
            "source_row_id",
            "source_raw",
            "imported_at",
            "observation_date",
            "category",
            "scope",
            "commodity",
            "location_code",
            "supplier",
            "quantity_value",
            "quantity_unit",
            "normalized_quantity",
            "normalized_unit",
            "activity_value",
            "activity_unit",
            "emission_kg_co2e",
            "cost_usd",
            "description",
            "status",
            "flagged_reasons",
            "last_modified_at",
        ]


class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = ["id", "record", "actor", "action", "notes", "created_at"]
