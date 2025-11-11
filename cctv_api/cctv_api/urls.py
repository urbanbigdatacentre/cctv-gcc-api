from django.shortcuts import redirect
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings

import cctv_api.views.api.tf2 as tf2_api_views
import cctv_api.views.api.yolo as yolo_api_views
import cctv_api.views.general as general_views

app_name = "cctv-api"

general_urls = (
    [
        path("cameras", lambda r: redirect(to="cctv-api:general:cameras-list")),
        path("cameras/", general_views.CameraViewSet.as_view(), name="cameras-list"),
        path(
            "cameras/<int:pk>",
            general_views.CameraViewDetail.as_view(),
            name="cameras-detail",
        ),
    ],
    "general",
)


tf2_urls = (
    [
        path("records", lambda r: redirect(to="cctv-api:tf2:records-list")),
        path("records/", tf2_api_views.TF2RecordsViewSet.as_view(), name="records-list"),
    ],
    "tf2",
)
yolo_urls = (
    [
        path("records", lambda r: redirect(to="cctv-api:yolo:records-list")),
        path("records/", yolo_api_views.YOLORecordsViewSet.as_view(), name="records-list"),
    ],
    "yolo",
)

urlpatterns = [
    path("", lambda r: redirect(to="cctv-api:api-docs")),
    path("general/", include(general_urls)),
    path("tf2/", include(tf2_urls)),
    path("yolo/", include(yolo_urls)),
    path("schema.yaml", SpectacularAPIView.as_view(custom_settings=settings.SPECTACULAR_DEFAULTS), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="cctv-api:schema"), name="api-docs"),
]
