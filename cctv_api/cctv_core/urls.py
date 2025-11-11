from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("cctv_records.urls")),
    path("", include("cctv_api.urls")),
]
