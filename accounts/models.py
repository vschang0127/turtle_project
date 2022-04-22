from django.contrib.auth.models import User
from django.db import models
from fitting.models import MyPhoto


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_pk = models.IntegerField(blank=True)
    nickname = models.CharField(max_length=200, blank=True)
    point = models.IntegerField(default=0)
    my_photo = models.ForeignKey(MyPhoto, null=True, blank=True, on_delete=models.CASCADE)
    fitting_photo = models.ImageField(null=True, upload_to="images/fitting_photo/", blank=True)
