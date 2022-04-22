from tkinter import CASCADE
from django.db import models


# Create your models here.

class Cloth(models.Model):
    id = models.IntegerField(primary_key=True)
    serial_number = models.CharField(max_length=10)
    color_number = models.CharField(max_length=5)
    color = models.CharField(max_length=20)
    cloth_name = models.CharField(max_length=50)
    cloth_price = models.BigIntegerField()
    gender = models.CharField(max_length=5)
    category = models.CharField(max_length=10)
    description = models.CharField(max_length=200)
    cloth_image = models.ImageField(null=True, upload_to="images/clothes/", blank=True)
    model_image = models.ImageField(null=True, upload_to="images/models/", blank=True)
    cloth_mask = models.ImageField(null=True, upload_to="images/clothes_mask/", blank=True)
    
    
    def __str__(self):
        return self.cloth_name

class FittingCloth(models.Model):
    id = models.IntegerField(primary_key=True)
    serial_number = models.CharField(max_length=10)
    color_number = models.CharField(max_length=5)
    color = models.CharField(max_length=20)
    cloth_name = models.CharField(max_length=50)
    cloth_price = models.BigIntegerField()
    gender = models.CharField(max_length=5)
    category = models.CharField(max_length=10)
    description = models.CharField(max_length=200)
    cloth_image = models.ImageField(null=True, upload_to="images/fitting_clothes/", blank=True)
    model_image = models.ImageField(null=True, upload_to="images/models/", blank=True)
    cloth_mask = models.ImageField(null=True, upload_to="images/clothes_mask/", blank=True)

class ChangedCloth(models.Model):
    cloth = models.ForeignKey(Cloth, on_delete=models.CASCADE)
    changed_color_r = models.IntegerField()
    changed_color_g = models.IntegerField()
    changed_color_b = models.IntegerField()
    changed_cloth = models.CharField(max_length=200)

class ClothPng(models.Model):
    id = models.IntegerField(primary_key=True)
    serial_number = models.CharField(max_length=10)
    color_number = models.CharField(max_length=5)
    color = models.CharField(max_length=20)
    cloth_name = models.CharField(max_length=50)
    cloth_price = models.BigIntegerField()
    gender = models.CharField(max_length=5)
    category = models.CharField(max_length=10)
    description = models.CharField(max_length=200)
    cloth_image = models.ImageField(null=True, upload_to="images/png_clothes/", blank=True)
    model_image = models.ImageField(null=True, upload_to="images/models/", blank=True)
    cloth_mask = models.ImageField(null=True, upload_to="images/clothes_mask/", blank=True)


class ChangedClothPng(models.Model):
    cloth = models.ForeignKey(ClothPng, on_delete=models.CASCADE)
    changed_color_r = models.IntegerField()
    changed_color_g = models.IntegerField()
    changed_color_b = models.IntegerField()
    changed_cloth = models.CharField(max_length=200)
