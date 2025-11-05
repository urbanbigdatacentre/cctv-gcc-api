from rest_framework import generics
from cctv_api.serializers.general import CameraGroupSerializer, CameraSerializer
from cctv_records.models import CameraGroups
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


class CameraGroupsViewSet(generics.ListAPIView):
    """
    ## Camera Groups
    """

    # schema = AutoSchema(tags=["general"])
    http_method_names = [
        "get",
        "options",
    ]
    serializer_class = CameraGroupSerializer
    queryset = CameraGroups.objects.order_by("id").exclude(id=1)


class CameraGroupsDetail(generics.RetrieveAPIView):
    # schema = AutoSchema(tags=["general"])
    serializer_class = CameraGroupSerializer
    queryset = CameraGroups.objects.all()
    http_method_names = [
        "get",
        "options",
    ]
