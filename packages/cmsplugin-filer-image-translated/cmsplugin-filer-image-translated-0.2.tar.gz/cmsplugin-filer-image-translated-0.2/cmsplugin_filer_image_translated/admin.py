"""Admin classes for the ``filer_image_translated`` app."""
from django.contrib import admin

from filer.admin.imageadmin import ImageAdmin
from filer.models import Image
from hvad.admin import TranslatableAdmin

from .models import ImageTranslation

ImageAdmin.fieldsets = None

admin.site.unregister(Image)
admin.site.register(Image, ImageAdmin)

admin.site.register(ImageTranslation, TranslatableAdmin)
