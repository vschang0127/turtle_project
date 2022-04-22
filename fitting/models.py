import os
import uuid

from django.conf import settings
from django.db import models
from upload_clothes.models import *


# 내 사진 저장
def change_uploaded_filename(instance, filename):
    path = "images/my_photo/"
    extension = filename.split(".")[-1]
    format = str(instance.user.username) + '_' + \
        str(uuid.uuid4()) + '.' + extension
    return os.path.join(path, format)


class MyPhoto(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    my_photo_title = models.CharField(
        max_length=255, null=True, default="a.jpg")
    my_photo = models.ImageField(
        null=True, upload_to=change_uploaded_filename, blank=True)


# 찜한 옷 저장
class MyPreferCloth(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    prefer_cloth_title = models.CharField(
        max_length=255, null=True, default="a.jpg")
    prefer_cloth = models.ForeignKey(Cloth, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.prefer_cloth.cloth_name


class MyFitting(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    my_photo = models.ForeignKey(MyPhoto, on_delete=models.CASCADE)
    cloth = models.ForeignKey(FittingCloth, on_delete=models.CASCADE)
    fitting_photo = models.CharField(max_length=255, null=True)

#test


class FittingTest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    my_photo = models.ImageField(
        null=True, upload_to="images/my_photo/", blank=True)
    my_prefer_cloth = models.ImageField(
        null=True, upload_to="images/clothes/", blank=True)
    fitting_photo = models.ImageField(
        null=True, upload_to="images/fitting_test/", blank=True)
