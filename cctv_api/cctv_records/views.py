import logging

from django.conf import settings
from django.db.models import F
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from .forms import UploadReportForm
from .models import CameraRecordsFile
from .utils import handle_uploaded_report_file

logger = logging.getLogger("cctv.views")


@csrf_exempt
def event(request: HttpRequest):
    if request.method == "POST":
        if "FILENAME-DOWNLOAD" in request.headers:
            filename = request.headers.get("filename-download")
            CameraRecordsFile.objects.filter(filename=filename).update(number_of_downloads=F("number_of_downloads") + 1)
            return JsonResponse(status=status.HTTP_200_OK, data={"result": "ok"})
    return JsonResponse(
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        data={"status_code": 422, "message": "not understood"},
    )


@csrf_exempt
def upload_report(request: HttpRequest):
    if request.method == "POST":
        pin_number = request.POST.get("pin-code")
        overwrite = request.POST.get("overwrite", False) == "t"
        if pin_number != settings.UPLOAD_REPORT_PIN:
            return JsonResponse(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"status_code": 401, "message": "unauthorized"},
            )
        form = UploadReportForm(request.POST, request.FILES)
        logger.info(request.FILES)
        r_data = {}
        for f in request.FILES.values():
            logger.info("processing file: %s", f)
            r = handle_uploaded_report_file(f, overwrite=overwrite)
            r_data.update(r)
        return JsonResponse(
            status=status.HTTP_200_OK,
            data=r_data,
        )

    form = UploadReportForm()
    return render(request, "cctv_records/upload_report.html", {"form": form})
