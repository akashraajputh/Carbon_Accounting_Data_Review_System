from django.contrib import admin
from django.urls import include, path
from dataapp.views import APIHomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", APIHomeView.as_view(), name="root-home"),
    path("api/", include("dataapp.urls")),
]
