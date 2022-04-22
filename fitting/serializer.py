from rest_framework import serializers

from .models import *


class MyPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = MyPhoto
        exclude = ['user']

    def get_username(self, obj):
        return obj.user.username


class MyPreferClothSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyPreferCloth
        fields = ('user', 'prefer_cloth_title', 'prefer_cloth')


class MyPreferClothListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cloth
        fields = ('id', 'serial_number', 'color_number',
                  'cloth_name', 'cloth_image', 'model_image')


class MyFittingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyFitting
        exclude = ['user']



class FittingTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FittingTest
        fields = '__all__'
