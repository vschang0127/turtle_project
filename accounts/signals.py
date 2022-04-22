from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from upload_clothes.models import Cloth

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, user_pk=instance.id, nickname=instance.username)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Cloth)
def update_prefer_cloth_profile(sender, instance, created, **kwargs):
    if created:
        instance.profile.save()
