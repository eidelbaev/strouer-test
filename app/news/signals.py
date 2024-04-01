from django.db.models.signals import post_save, pre_delete       
from django.dispatch import receiver

from .models import Comment, Post


@receiver(post_save, sender=Comment)
@receiver(post_save, sender=Post)
def log_model_update(sender, instance, created, **kwargs):
    if created:
        instance.log_created()
    else:
        instance.log_updated()


@receiver(pre_delete, sender=Comment)
@receiver(pre_delete, sender=Post)
def log_model_delete(sender, instance, **kwargs):
    instance.log_deleted()
