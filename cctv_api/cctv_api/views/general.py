from rest_framework import generics
from cctv_api.serializers.general import CameraSerializer
from cctv_records.utils import get_cameras_that_have_records


class CameraViewSet(generics.ListAPIView):
    """
    ##  Camera Locations
    """

    # schema = AutoSchema(tags=["general"])
    queryset = get_cameras_that_have_records()
    serializer_class = CameraSerializer
    pagination_class = None
    http_method_names = [
        "get",
        "options",
    ]


class CameraViewDetail(generics.RetrieveAPIView):
    """
    ##  Camera Detail
    """

    http_method_names = [
        "get",
        "options",
    ]
    # schema = AutoSchema(tags=["general"])
    queryset = get_cameras_that_have_records()
    serializer_class = CameraSerializer
