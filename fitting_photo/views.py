import torch.nn as nn
from django.http import QueryDict
from fitting.models import *
from fitting.serializer import *
from rest_framework import status, viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from turtle_app.settings import *

from fitting_photo.models.afwm import AFWM
from fitting_photo.models.networks import ResUnetGenerator, load_checkpoint
from fitting_photo.options.test_options import TestOptions

from .run_model import run_model

opt = TestOptions().parse()

# 모델정의
warp_model = AFWM(opt, 3)
warp_model.eval()
warp_model.cuda()
load_checkpoint(
    warp_model, '/home/ubuntu/django/turtle_app/fitting_photo/checkpoints/PFAFN/warp_model_final.pth')
gen_model = ResUnetGenerator(7, 4, 5, ngf=64, norm_layer=nn.BatchNorm2d)
gen_model.eval()
gen_model.cuda()
load_checkpoint(
    gen_model, '/home/ubuntu/django/turtle_app/fitting_photo/checkpoints/PFAFN/gen_model_final.pth')


@permission_classes([AllowAny])
class MyFittingClothViewSet(viewsets.ModelViewSet):
    serializer_class = MyFittingSerializer

    def show_list(self, request):
        user = self.request.user
        query_set = MyFitting.objects.filter(user=user)

        query_list = []

        for query in query_set:
            
            query_dict = {}
            query_dict['id'] = query.id
            query_dict['cloth'] = query.cloth
            query_dict['my_photo'] = query.my_photo
            query_dict['fitting_photo'] = query.fitting_photo

            query_list.append(query_dict)

        serializer = MyFittingSerializer(query_list, many=True)

        return Response(serializer.data)

    def create(self, request):
        data = request.data
        my_photo_id = data.get('my_photo_id')
        cloth_id = data.get('cloth_id')

        user = self.request.user
        user_pk = user.pk
        username = user.username
        my_photo = MyPhoto.objects.get(id=my_photo_id)
        my_photo_name = str(my_photo.my_photo).split('/')[-1].split('.')[0]
        cloth = FittingCloth.objects.get(id=cloth_id)

        img_url = my_photo.my_photo
        cloth_url = cloth.cloth_image

        cloth_url_list = str(cloth_url).split('/')
        cloth_file_name = cloth_url_list[-1]

        edge_url = cloth.cloth_mask
        result_path = f'images/fitting_photo/{username}'

        opt.img_url = img_url
        opt.cloth_url = cloth_url
        opt.edge_url = edge_url
        opt.result_path = result_path

        run_model(opt, warp_model, gen_model)

        #-----------------------------------------------------------------------

        fitting_photo_url = f'{MEDIA_URL}{result_path}/{my_photo_name}_{cloth_file_name}'
        image_url = f'{MEDIA_URL}' + str(img_url)
        cloth_full_url = f'{MEDIA_URL}' + str(cloth_url)

        query = {}
        query['user'] = user_pk
        query['my_photo'] = my_photo.id
        query['cloth'] = cloth.id
        query['fitting_photo'] = fitting_photo_url

        if not MyFitting.objects.filter(user=user_pk, fitting_photo=fitting_photo_url).exists():
            query_dict = QueryDict('', mutable=True)
            query_dict.update(query)
            serializer = MyFittingSerializer(
                data=query_dict, context={'request': request})

            if serializer.is_valid():
                serializer.save(user=user)
                context = {
                    'my_photo': image_url,
                    'cloth': cloth_full_url,
                    'fitting_photo': fitting_photo_url
                }
                return Response(context, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Already exists Fitting Photo', status=status.HTTP_400_BAD_REQUEST)
