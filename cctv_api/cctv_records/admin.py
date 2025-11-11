from django.contrib import admin

from .models import Cameras

admin.site.empty_value_display = "(None)"


class CameraAdmin(admin.ModelAdmin):
    empty_value_display = "unknown"
    list_filter = ["is_complete"]
    list_display = ["__str__", "label", "is_complete"]
    ordering = ["is_complete"]


admin.site.register(Cameras, CameraAdmin)
