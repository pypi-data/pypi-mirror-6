"""Tests for the models of the cmsplugin_filer_image_translated app."""
from django.test import TestCase

from filer.models import Image

from ..models import ImageTranslation


class ImageTranslationTestCase(TestCase):
    """Test for the `ImageTranslation` model class."""
    longMessage = True

    def test_auto_creation_and_deletion(self):
        # We need to test, if a ImageTranslation is instantly created when an
        # Image is created
        image = Image.objects.create()
        self.assertEqual(ImageTranslation.objects.count(), 1, msg=(
            'The ImageTranslation was not created properly.'))

        # An ImageTranslation should not be created again, when the image is
        # saved again
        image.save()
        self.assertEqual(ImageTranslation.objects.count(), 1, msg=(
            'The amount of ImageTranslations should not have changed.'))

        # An ImageTranslation should be deleted again, when the Image is
        # deleted
        image.delete()
        self.assertEqual(ImageTranslation.objects.count(), 0, msg=(
            'The ImageTranslation should have been deleted together with the'
            ' Image.'))
