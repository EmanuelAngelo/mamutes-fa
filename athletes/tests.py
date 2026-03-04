import shutil
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from PIL import Image

from .models import Athlete


class AthletePhotoProcessingTests(TestCase):
	def setUp(self):
		self._tmp_media = tempfile.mkdtemp(prefix="mamutes_media_")

	def tearDown(self):
		shutil.rmtree(self._tmp_media, ignore_errors=True)

	@override_settings(
		MEDIA_ROOT=None,
		ATHLETE_PHOTO_MAX_SIDE=256,
		ATHLETE_PHOTO_MAX_BYTES=200_000,
		ATHLETE_PHOTO_JPEG_QUALITY=85,
		ATHLETE_PHOTO_JPEG_QUALITY_MIN=45,
	)
	def test_photo_is_resized_and_converted_to_jpeg(self):
		# Ensure MEDIA_ROOT is isolated for this test
		with override_settings(MEDIA_ROOT=self._tmp_media):
			img = Image.new("RGB", (2000, 1200), (120, 10, 10))
			buf = BytesIO()
			img.save(buf, format="PNG")
			uploaded = SimpleUploadedFile(
				"athlete.png",
				buf.getvalue(),
				content_type="image/png",
			)

			a = Athlete.objects.create(name="Teste", photo=uploaded)

			a.refresh_from_db()
			self.assertTrue(a.photo.name.lower().endswith(".jpg"))

			a.photo.open("rb")
			try:
				with Image.open(a.photo.file) as saved:
					self.assertEqual(saved.format, "JPEG")
					w, h = saved.size
					self.assertLessEqual(max(w, h), 256)
			finally:
				a.photo.close()
