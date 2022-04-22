from django.http import QueryDict
from rest_framework import status, viewsets
from rest_framework.decorators import permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import *
from .serializer import *


# Create your views here.
@permission_classes([AllowAny])
class MyPhotoViewSet(viewsets.ModelViewSet):
    serializer_class = MyPhotoSerializer
    parser_classes = (MultiPartParser, FormParser)

    def show_list(self, request):
        user = self.request.user
        query_set = MyPhoto.objects.filter(user=user)

        serializer = MyPhotoSerializer(query_set, many=True)

        return Response(serializer.data)

    def create(self, request):
        data = request.data

        data['user'] = self.request.user
        data['my_photo_title'] = request.FILES.get(
            'my_photo').name.split('.')[0]

        #file 이름 변경

        query_dict = QueryDict('', mutable=True)
        query_dict.update(data)
        serializer = MyPhotoSerializer(
            data=query_dict, context={'request': request})

        if serializer.is_valid():
            serializer.save(user=self.request.user)

            return Response('Upload My Photo Successfully!!', status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        data = request.data
        my_photo_id = data.get('id')
        user = self.request.user
        delete_my_photo = MyPhoto.objects.filter(id=my_photo_id, user=user)

        if delete_my_photo.exists():
            delete_my_photo.delete()
            return Response('Delete Successfully!!', status=status.HTTP_201_CREATED)
        else:
            return Response('Not exists My Photo', status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class MyPreferClothViewSet(viewsets.ModelViewSet):
    serializer_class = MyPreferClothListSerializer

    def show_list(self, request):
        user = self.request.user
        query_set = MyPreferCloth.objects.filter(user=user)

        query_list = []

        for query in query_set:
            cloth = query.prefer_cloth
            query_dict = {}
            query_dict['id'] = cloth.id
            query_dict['serial_number'] = cloth.serial_number
            query_dict['color_number'] = cloth.color_number
            query_dict['cloth_name'] = cloth.cloth_name
            query_dict['cloth_image'] = cloth.cloth_image
            query_dict['model_image'] = cloth.model_image
            query_list.append(query_dict)

        serializer = MyPreferClothListSerializer(query_list, many=True)

        return Response(serializer.data)

    def create(self, request):
        data = request.data

        serial_number = data.get('serial_number')
        color_number = data.get('color_number')

        user = self.request.user
        cloth = Cloth.objects.get(
            serial_number=serial_number, color_number=color_number)
        user_pk = user.pk
        cloth_pk = cloth.pk

        query = {}
        query['user'] = user_pk
        query['prefer_cloth_title'] = cloth.cloth_name + '_' + cloth.color
        query['prefer_cloth'] = cloth_pk

        if not MyPreferCloth.objects.filter(user=user_pk, prefer_cloth=cloth_pk).exists():
            query_dict = QueryDict('', mutable=True)
            query_dict.update(query)
            serializer = MyPreferClothSerializer(
                data=query_dict, context={'request': request})

            if serializer.is_valid():
                serializer.save(user=user)

                return Response('Save successfully!!', status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Already exists Prefer Cloth', status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        data = request.data
        user = self.request.user
        cloth_id = data.get('cloth_id')
        delete_cloth = MyPreferCloth.objects.filter(
            user=user, prefer_cloth=cloth_id)
        if delete_cloth.exists():
            delete_cloth.delete()
            return Response('Delete Successfully!!', status=status.HTTP_201_CREATED)
        else:
            return Response('Not exists Prefer Cloth', status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class FittingViewSet(viewsets.ModelViewSet):
    serializer_class = FittingTestSerializer

    def show_list(self, request):
        user = self.request.user
        query_set = FittingTest.objects.all()

        serializer = FittingTestSerializer(query_set, many=True)

        return Response(serializer.data)
