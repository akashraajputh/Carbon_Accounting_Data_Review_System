from django.urls import path
from .views import APIHomeView, AuditEventList, EmissionRecordList, ImportBatchList, ImportDataView, RecordActionView, TenantList

urlpatterns = [
    path("", APIHomeView.as_view(), name="api-home"),
    path("tenants/", TenantList.as_view(), name="tenant-list"),
    path("import/", ImportDataView.as_view(), name="import-data"),
    path("records/", EmissionRecordList.as_view(), name="record-list"),
    path("records/<int:pk>/action/", RecordActionView.as_view(), name="record-action"),
    path("batches/", ImportBatchList.as_view(), name="batch-list"),
    path("audit/", AuditEventList.as_view(), name="audit-list"),
]
