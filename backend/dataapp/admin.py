from django.contrib import admin
from .models import AuditEvent, EmissionRecord, ImportBatch, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ("source_name", "tenant", "uploaded_at", "row_count")
    list_filter = ("source_type",)


@admin.register(EmissionRecord)
class EmissionRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "tenant", "source_type", "category", "scope", "status", "emission_kg_co2e")
    list_filter = ("status", "scope", "source_type")
    search_fields = ("source_row_id", "commodity", "location_code", "supplier")


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("record", "action", "actor", "created_at")
    list_filter = ("action",)
