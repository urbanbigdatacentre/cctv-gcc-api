from datetime import datetime
from logging import getLogger

from pydantic import BaseModel, constr

logger = getLogger(__name__)


class CommonMethodsMixin:
    @property
    def csv_line(self):
        raise NotImplementedError()

    def to_db_record(self, camera_id=None):
        raise NotImplementedError()


class TF2ReportRecord(BaseModel, CommonMethodsMixin):
    image_proc: datetime
    image_capt: datetime
    camera_ref: constr(to_lower=True, strip_whitespace=True)  # type: ignore
    model_name: constr(to_lower=True, strip_whitespace=True)  # type: ignore
    car: int
    person: int
    bicycle: int
    motorcycle: int
    bus: int
    truck: int
    warnings: None | int

    @property
    def cars(self):
        return self.car

    @property
    def camera_id(self):
        return self.camera_ref

    @property
    def persons(self):
        return self.person

    @property
    def bicycles(self):
        return self.bicycle

    @property
    def motorcycles(self):
        return self.motorcycle

    @property
    def buses(self):
        return self.bus

    @property
    def trucks(self):
        return self.truck

    @property
    def camera_ok(self) -> None | bool:
        if self.warnings is None:
            return None
        return not bool(self.warnings)

    @property
    def csv_line(self):
        image_proc_str = self.image_proc.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        image_capt_str = self.image_proc.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        return f"{image_proc_str},{image_capt_str},{self.camera_ref},{self.model_name},{self.car},{self.person},{self.bicycle},{self.motorcycle},{self.bus},{self.truck},{self.warnings}\n"

    def to_db_record(self, camera_id=None):
        from cctv_records.models import Cameras, TF2Records

        c, created = Cameras.objects.get_or_create(camera_id=camera_id or self.camera_ref)
        if created:
            logger.warning(f"Created camera {c}")

        return TF2Records(
            timestamp=self.image_capt,
            cars=self.car,
            persons=self.person,
            bicycles=self.bicycle,
            motorcycles=self.motorcycle,
            buses=self.bus,
            trucks=self.truck,
            camera_ok=self.camera_ok,
            camera=c,
        )


class YOLOReportRecord(BaseModel, CommonMethodsMixin):
    image_proc: datetime
    image_capt: datetime
    camera_ref: constr(to_lower=True, strip_whitespace=True)  # type: ignore
    model_name: constr(to_lower=True, strip_whitespace=True)  # type: ignore
    car: int
    pedestrian: int
    cyclist: int
    motorcycle: int
    bus: int
    lorry: int
    van: int
    taxi: int
    warnings: None | int

    @property
    def camera_id(self):
        return self.camera_ref

    @property
    def cars(self):
        return self.car

    @property
    def pedestrians(self):
        return self.pedestrian

    @property
    def cyclists(self):
        return self.cyclist

    @property
    def motorcycles(self):
        return self.motorcycle

    @property
    def buses(self):
        return self.bus

    @property
    def lorries(self):
        return self.lorry

    @property
    def vans(self):
        return self.van

    @property
    def taxis(self):
        return self.taxi

    @property
    def camera_ok(self) -> None | bool:
        if self.warnings is None:
            return None
        return not bool(self.warnings)

    @property
    def csv_line(self):
        image_proc_str = self.image_proc.strftime("%Y-%m-%d %H:%M:%S.%f%z")
        image_capt_str = self.image_proc.strftime("%Y-%m-%d %H:%M:%S.%f%z")

        return f"{image_proc_str},{image_capt_str},{self.camera_ref},{self.model_name},{self.car},{self.pedestrian},{self.cyclist},{self.motorcycle},{self.bus},{self.lorry},{self.van},{self.taxi},{self.warnings}\n"

    def to_db_record(self, camera_id=None):
        from cctv_records.models import Cameras, YOLORecords

        c, created = Cameras.objects.get_or_create(camera_id=camera_id or self.camera_ref)
        if created:
            logger.warning(f"Created camera {c}")
        return YOLORecords(
            timestamp=self.image_capt,
            cars=self.cars,
            pedestrians=self.pedestrians,
            cyclists=self.cyclists,
            motorcycles=self.motorcycles,
            buses=self.buses,
            lorries=self.lorries,
            vans=self.vans,
            taxis=self.taxis,
            camera_ok=self.camera_ok,
            camera=c,
        )


__all__ = ["TF2ReportRecord", "YOLOReportRecord"]
