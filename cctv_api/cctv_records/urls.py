from django.urls import path

from . import views

app_name = "cctv-records"

urlpatterns = [
    path("event/", views.event),
    path("event", views.event, name="event"),
    path("upload_report", views.upload_report, name="upload-report"),
]
