from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Play


@receiver(post_delete, sender=Play)
def delete_play_image_file_on_delete(sender, instance: Play, **kwargs):
    """Delete the image file from storage when the Play is deleted."""
    if instance.image:
        try:
            instance.image.delete(save=False)
        except Exception:
            # best-effort cleanup
            pass


@receiver(pre_save, sender=Play)
def delete_old_image_file_on_change(sender, instance: Play, **kwargs):
    """Delete old image file when image is replaced or cleared."""
    if not instance.pk:
        return

    try:
        old = Play.objects.get(pk=instance.pk)
    except Play.DoesNotExist:
        return

    old_file = old.image
    new_file = instance.image

    # If old had a file and new is empty => delete old.
    if old_file and not new_file:
        try:
            old_file.delete(save=False)
        except Exception:
            pass
        return

    # If both exist and changed => delete old.
    if old_file and new_file and old_file.name != new_file.name:
        try:
            old_file.delete(save=False)
        except Exception:
            pass
