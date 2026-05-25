from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditEvent, EmissionRecord, ImportBatch, Tenant
from .serializers import AuditEventSerializer, EmissionRecordSerializer, ImportBatchSerializer, TenantSerializer
from .utils import parse_sap_rows, parse_travel_rows, parse_utility_rows

SOURCE_PARSERS = {
    "sap": parse_sap_rows,
    "utility": parse_utility_rows,
    "travel": parse_travel_rows,
}

SOURCE_NAMES = {
    "sap": "SAP Fuel & Procurement",
    "utility": "Utility Electricity",
    "travel": "Corporate Travel",
}


class TenantList(generics.ListAPIView):
    queryset = Tenant.objects.all().order_by("slug")
    serializer_class = TenantSerializer


class APIHomeView(APIView):
    def get(self, request):
        return Response({
            "detail": "Carbon intake API",
            "endpoints": {
                "tenants": "/api/tenants/",
                "import": "/api/import/",
                "records": "/api/records/",
                "batches": "/api/batches/",
                "audit": "/api/audit/",
            },
        })


@method_decorator(csrf_exempt, name="dispatch")
class ImportDataView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        tenant_slug = request.data.get("tenant_slug")
        source_type = request.data.get("source_type")
        file_obj = request.FILES.get("file")
        if not tenant_slug or not source_type or not file_obj:
            return Response({"detail": "tenant_slug, source_type, and file are required."}, status=status.HTTP_400_BAD_REQUEST)
        tenant = get_object_or_404(Tenant, slug=tenant_slug)
        source_type = source_type.lower()
        parser = SOURCE_PARSERS.get(source_type)
        if parser is None:
            return Response({"detail": "Unsupported source_type."}, status=status.HTTP_400_BAD_REQUEST)
        rows = parser(file_obj)
        batch = ImportBatch.objects.create(
            tenant=tenant,
            source_name=SOURCE_NAMES.get(source_type, source_type.title()),
            source_type=source_type,
            original_filename=file_obj.name,
            row_count=len(rows),
            source_details={"submitted_by": request.user.username if request.user.is_authenticated else "anonymous"},
        )
        records = []
        for row in rows:
            record = EmissionRecord.objects.create(
                tenant=tenant,
                batch=batch,
                source_type=source_type,
                source_name=batch.source_name,
                source_row_id=row.get("source_row_id", ""),
                source_raw=row.get("source_raw", {}),
                observation_date=row.get("observation_date"),
                category=row["category"],
                scope=row["scope"],
                commodity=row.get("commodity", ""),
                location_code=row.get("location_code", ""),
                supplier=row.get("supplier", ""),
                quantity_value=row.get("quantity_value"),
                quantity_unit=row.get("quantity_unit", ""),
                normalized_quantity=row.get("normalized_quantity"),
                normalized_unit=row.get("normalized_unit", ""),
                emission_kg_co2e=row.get("emission_kg_co2e"),
                cost_usd=row.get("cost_usd"),
                description=row.get("description", ""),
                flagged_reasons=row.get("flagged_reasons", []),
            )
            records.append(record)
        serializer = ImportBatchSerializer(batch)
        return Response({"batch": serializer.data, "inserted": len(records)}, status=status.HTTP_201_CREATED)


class EmissionRecordList(generics.ListAPIView):
    serializer_class = EmissionRecordSerializer

    def get_queryset(self):
        queryset = EmissionRecord.objects.select_related("tenant", "batch").order_by("-imported_at")
        tenant_slug = self.request.query_params.get("tenant_slug")
        status_filter = self.request.query_params.get("status")
        flagged = self.request.query_params.get("flagged")
        if tenant_slug:
            queryset = queryset.filter(tenant__slug=tenant_slug)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if flagged == "true":
            queryset = queryset.exclude(flagged_reasons=[])
        return queryset


@method_decorator(csrf_exempt, name="dispatch")
class RecordActionView(APIView):
    def post(self, request, pk):
        action = request.data.get("action")
        if action not in ["approve", "reject"]:
            return Response({"detail": "action must be approve or reject."}, status=status.HTTP_400_BAD_REQUEST)
        record = get_object_or_404(EmissionRecord, pk=pk)
        record.status = "approved" if action == "approve" else "rejected"
        record.last_modified_by = request.user if request.user.is_authenticated else None
        record.save()
        AuditEvent.objects.create(
            record=record,
            actor=request.user if request.user.is_authenticated else None,
            action=action,
            notes=request.data.get("notes", ""),
        )
        serializer = EmissionRecordSerializer(record)
        return Response(serializer.data)


class ImportBatchList(generics.ListAPIView):
    queryset = ImportBatch.objects.select_related("tenant").order_by("-uploaded_at")
    serializer_class = ImportBatchSerializer


class AuditEventList(generics.ListAPIView):
    queryset = AuditEvent.objects.select_related("record", "actor").order_by("-created_at")
    serializer_class = AuditEventSerializer
