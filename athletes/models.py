from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models

from PIL import Image, ImageOps

from io import BytesIO
import os

class Athlete(models.Model):
    class Position(models.TextChoices):
        QUARTERBACK = "QB", "Quarterback"
        CENTER = "C", "Center"
        WIDE_RECEIVER = "WR", "Wide receiver"
        RUNNING_BACK = "RB", "Running back"
        DEFENSIVE_BACK = "DB", "Defensive back"
        BLITZ_RUSHER = "R", "Blitz/Rusher"
        SAFETY = "S", "Safety"
        CORNER_BACK = "CB", "Corne back"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="athlete",
        help_text="Vincule um usuário para permitir login do atleta."
    )

    name = models.CharField(max_length=120)
    jersey_number = models.PositiveIntegerField(null=True, blank=True)

    photo = models.ImageField(upload_to="athletes/photos/", null=True, blank=True)

    birth_date = models.DateField(null=True, blank=True)
    birth_city = models.CharField(max_length=120, null=True, blank=True)

    height_m = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    current_position = models.CharField(max_length=5, choices=Position.choices, null=True, blank=True)
    desired_position = models.CharField(max_length=5, choices=Position.choices, null=True, blank=True)

    career_notes = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def _photo_limits(self):
        max_bytes = int(getattr(settings, "ATHLETE_PHOTO_MAX_BYTES", 10 * 1024 * 1024))
        max_side = int(getattr(settings, "ATHLETE_PHOTO_MAX_SIDE", 1600))
        jpeg_quality = int(getattr(settings, "ATHLETE_PHOTO_JPEG_QUALITY", 85))
        jpeg_quality_min = int(getattr(settings, "ATHLETE_PHOTO_JPEG_QUALITY_MIN", 45))
        return max_bytes, max_side, jpeg_quality, jpeg_quality_min

    def _needs_photo_processing(self, max_bytes: int, max_side: int) -> bool:
        if not self.photo:
            return False
        try:
            if getattr(self.photo, "size", 0) and int(self.photo.size) > max_bytes:
                return True
        except Exception:
            pass

        # If file is already small enough, still check dimensions.
        try:
            self.photo.file.seek(0)
            with Image.open(self.photo.file) as img:
                w, h = img.size
                return max(w, h) > max_side
        except Exception:
            return False

    def _process_photo(self):
        max_bytes, max_side, q0, qmin = self._photo_limits()
        if not self.photo or not getattr(self.photo, "file", None):
            return
        if not self._needs_photo_processing(max_bytes=max_bytes, max_side=max_side):
            return

        try:
            self.photo.file.seek(0)
            with Image.open(self.photo.file) as img0:
                img = ImageOps.exif_transpose(img0)

                # Convert to RGB (JPEG) and drop alpha if present.
                if img.mode in ("RGBA", "LA"):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[-1])
                    img = bg
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                # Resize to fit max_side.
                if max(img.size) > max_side:
                    img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

                # Encode as JPEG, reducing quality until under max_bytes.
                quality = q0
                out = BytesIO()
                while True:
                    out.seek(0)
                    out.truncate(0)
                    img.save(out, format="JPEG", quality=quality, optimize=True, progressive=True)
                    size = out.tell()
                    if size <= max_bytes or quality <= qmin:
                        break
                    quality = max(qmin, quality - 7)

                base, _ext = os.path.splitext(os.path.basename(self.photo.name or "photo"))
                new_name = f"{base}.jpg"
                self.photo.save(new_name, ContentFile(out.getvalue()), save=False)
        except Exception:
            # Fail-safe: never block saving athlete due to image processing.
            return

    def save(self, *args, **kwargs):
        self._process_photo()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name