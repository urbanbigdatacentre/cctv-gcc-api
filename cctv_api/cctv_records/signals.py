from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CameraGroups, Cameras


@receiver(post_save, sender=Cameras)
def create_camera_location(sender, instance: Cameras, created, **kwargs):
    if created:
        default_group = CameraGroups.get_default_group()
        instance.add_to_camera_groups(
            [
                default_group,
            ]
        )
