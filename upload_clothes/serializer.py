from rest_framework import serializers
from .models import *


class ClothSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cloth
        fields = '__all__'

class ChangedClothSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangedCloth
        fields = '__all__'

class ChangedClothPngSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangedClothPng
        fields = '__all__'
