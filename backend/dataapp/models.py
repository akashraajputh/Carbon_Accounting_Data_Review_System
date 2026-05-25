from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

class Tenant(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class ImportBatch(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="batches")
    source_name = models.CharField(max_length=120)
    source_type = models.CharField(max_length=80)
    uploaded_at = models.DateTimeField(default=timezone.now)
    original_filename = models.CharField(max_length=255)
    row_count = models.IntegerField(default=0)
    source_details = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.source_name} - {self.tenant.slug} - {self.uploaded_at.date()}"

class EmissionRecord(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    SCOPE_1 = "scope_1"
    SCOPE_2 = "scope_2"
    SCOPE_3 = "scope_3"
    SCOPE_CHOICES = [
        (SCOPE_1, "Scope 1"),
        (SCOPE_2, "Scope 2"),
        (SCOPE_3, "Scope 3"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="records")
    batch = models.ForeignKey(ImportBatch, on_delete=models.SET_NULL, null=True, related_name="records")
    source_type = models.CharField(max_length=80)
    source_name = models.CharField(max_length=120)
    source_row_id = models.CharField(max_length=255, blank=True)
    source_raw = models.JSONField(default=dict, blank=True)
    imported_at = models.DateTimeField(default=timezone.now)
    observation_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=120)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    commodity = models.CharField(max_length=120, blank=True)
    location_code = models.CharField(max_length=120, blank=True)
    supplier = models.CharField(max_length=200, blank=True)
    quantity_value = models.FloatField(null=True, blank=True)
    quantity_unit = models.CharField(max_length=40, blank=True)
    normalized_quantity = models.FloatField(null=True, blank=True)
    normalized_unit = models.CharField(max_length=40, blank=True)
    activity_value = models.FloatField(null=True, blank=True)
    activity_unit = models.CharField(max_length=40, blank=True)
    emission_kg_co2e = models.FloatField(null=True, blank=True)
    cost_usd = models.FloatField(null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    flagged_reasons = models.JSONField(default=list, blank=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="modified_records")

    def __str__(self):
        return f"{self.category} / {self.source_type} / {self.tenant.slug}"

class AuditEvent(models.Model):
    record = models.ForeignKey(EmissionRecord, on_delete=models.CASCADE, related_name="audit_events")
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=80)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.action} @ {self.record.id}"
