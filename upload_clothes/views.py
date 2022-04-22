import os

import boto3
import cv2
import numpy as np
from django.http import QueryDict
from PIL import Image
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from turtle_app.settings import *

from .models import *
from .serializer import *


# Create your views here.
@api_view(['GET', 'POST'])
def cloth_total(request):
    clothes = Cloth.objects.all()
    serializer = ClothSerializer(clothes, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def cloth_list(request):
    if request.method == 'POST':
        json = request.data
        gender = json['gender']
        category = json['category']
        clothes = Cloth.objects.filter(
            gender__icontains=gender, category__icontains=category)
        serializer = ClothSerializer(clothes, many=True)
        return Response(serializer.data)
#----------------------------------------------------------------------------------------------


@permission_classes([AllowAny])
class ChangedClothViewSet(viewsets.ModelViewSet):
    serializer_class = ChangedClothSerializer

    def show_list(self, request):
        query_set = ChangedCloth.objects.filter(
            cloth=request.data.get('cloth_id'))
        query_list = []
        for query in query_set:
            cloth = query.cloth.cloth_image
            query_dict = {}
            query_dict['id'] = query.id
            query_dict['cloth'] = cloth.cloth_image
            query_dict['changed_cloth'] = query.changed_cloth_image
            query_dict['changed_color_r'] = query.changed_color_r
            query_dict['changed_color_g'] = query.changed_color_g
            query_dict['changed_color_b'] = query.changed_color_b
            query_list.append(query_dict)
        serializer = ChangedClothSerializer(query_list, many=True)
        return Response(serializer.data)

    def change_color(self, request):
        data = request.data
        cloth_id = data.get('cloth_id')
        color_r = int(data.get('color_r'))
        color_g = int(data.get('color_g'))
        color_b = int(data.get('color_b'))
        if color_r < 16:
            hex_color_r = '0' + str(hex(color_r))[-1:]
        else:
            hex_color_r = str(hex(color_r))[-2:]
        if color_r < 16:
            hex_color_g = '0' + str(hex(color_g))[-1:]
        else:
            hex_color_g = str(hex(color_g))[-2:]
        if color_r < 16:
            hex_color_b = '0' + str(hex(color_b))[-1:]
        else:
            hex_color_b = str(hex(color_b))[-2:]
        color_hex = hex_color_r + hex_color_g + hex_color_b
        cloth = Cloth.objects.get(id=cloth_id)
        original_cloth_path = cloth.cloth_image
        changed_cloth_path = f'images/change_color'
        cloth_url_list = str(original_cloth_path).split('/')
        cloth_name = cloth_url_list[-1]
        changed_cloth_name = f'{color_hex}_{cloth_name}'
        os.makedirs(changed_cloth_path, exist_ok=True)

        def normalizer(x):  # rgb 값 0, 255 사이로 남을수있게 조절하기
            x = np.where(x > 255, 255, x)
            x = np.where(x < 5, 0, x)
            return x

        def colorswap(cloth_dir, res_dir, cloth_name, target_color):  # 색깔바꾸기 메인 함수
            s3 = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            
            )
            original_image=Image.open(cloth_dir).convert('RGBA')
            original_image_np=np.array(original_image)
            rgb_img_np=original_image_np[:,:,0:3]
            og_a = original_image_np[:,:,3]


            swap_image = rgb_img_np.astype(float)
            swap_image = swap_image - get_base_value(rgb_img_np,'mean')
            swap_image = normalizer(swap_image + target_color)
            #완성 이미지 1차 저장
            final_image = swap_image.astype(np.uint8)
            final_b, final_g, final_r = cv2.split(final_image)
            final_image_alpha = cv2.merge((final_b,final_g,final_r,og_a))
            Pillow_img=Image.fromarray(final_image_alpha)
            white_np=np.ones((512,384),dtype=np.uint8)*255
            white_img=Image.fromarray(white_np).convert('RGBA')
            real_final=Image.alpha_composite(white_img,Pillow_img)
            real_final.save(res_dir + '/' + cloth_name)
            s3.upload_file(
                res_dir + '/' + cloth_name, AWS_STORAGE_BUCKET_NAME, 'media/' + res_dir + '/' + changed_cloth_name)

        # 관심지억 선언후 'mean','max', 또는 'min' 색깔 값 가져오기
        def get_base_value(original_image, return_type):
            #관심지억 선언하기
            roi = original_image[180:200, 240:260]
            roi_w, roi_h = roi.shape[:2]
            #3차원 배열 2차원으로 바꿔주기
            roi_reshape = np.reshape(roi, (roi_w * roi_h, 3))
            #배열의 sum구해서 max, min 색값의 index 찾고 저장하기
            roi_sum = np.sum(roi_reshape.astype(float), axis=1)
            roi_max = roi_reshape[np.argmax(roi_sum)]
            roi_min = roi_reshape[np.argmin(roi_sum)]
            #argument로 max, min, 또는 mean 선택할수있게 하기
            if return_type == 'mean':
                target_value = np.mean([roi_max, roi_min], axis=0)
            else:
                print('get_base_value: invalid target value')
            return target_value
        target_color = [color_r, color_g, color_b]
        colorswap(original_cloth_path, changed_cloth_path,
                  changed_cloth_name, target_color)
        changed_cloth_url = f'{MEDIA_URL}{changed_cloth_path}/{changed_cloth_name}'
        cloth_full_url = f'{MEDIA_URL}' + str(original_cloth_path)
        query = {}
        query['changed_cloth'] = changed_cloth_url
        query['cloth'] = cloth.id
        query['changed_color_r'] = color_r
        query['changed_color_g'] = color_g
        query['changed_color_b'] = color_b
        if not ChangedCloth.objects.filter(changed_cloth=changed_cloth_url).exists():
            query_dict = QueryDict('', mutable=True)
            query_dict.update(query)
            serializer = ChangedClothSerializer(
                data=query_dict, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                context = {
                    'changed_cloth': changed_cloth_url,
                    'cloth': cloth_full_url,
                    'color': '##' + color_hex + f' (r, g, b)=({color_r}, {color_g}, {color_b})'
                }
                return Response(context, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Already exists Color Cloth', status=status.HTTP_400_BAD_REQUEST)


#------------------------------------------------------------------------------------------
#PNG
@permission_classes([AllowAny])
class ChangedClothPngViewSet(viewsets.ModelViewSet):
    serializer_class = ChangedClothPngSerializer

    def show_list(self, request):
        query_set = ChangedClothPng.objects.filter(
            cloth=request.data.get('cloth_id'))
        query_list = []
        for query in query_set:
            cloth = query.cloth.cloth_image
            query_dict = {}
            query_dict['id'] = query.id
            query_dict['cloth'] = cloth.cloth_image
            query_dict['changed_cloth'] = query.changed_cloth_image
            query_dict['changed_color_r'] = query.changed_color_r
            query_dict['changed_color_g'] = query.changed_color_g
            query_dict['changed_color_b'] = query.changed_color_b
            query_list.append(query_dict)
        serializer = ChangedClothPngSerializer(query_list, many=True)
        return Response(serializer.data)

    def change_color(self, request):
        data = request.data
        cloth_id = data.get('cloth_id')
        color_r = int(data.get('color_r'))
        color_g = int(data.get('color_g'))
        color_b = int(data.get('color_b'))
        if color_r < 16:
            hex_color_r = '0' + str(hex(color_r))[-1:]
        else:
            hex_color_r = str(hex(color_r))[-2:]
        if color_r < 16:
            hex_color_g = '0' + str(hex(color_g))[-1:]
        else:
            hex_color_g = str(hex(color_g))[-2:]
        if color_r < 16:
            hex_color_b = '0' + str(hex(color_b))[-1:]
        else:
            hex_color_b = str(hex(color_b))[-2:]
        color_hex = hex_color_r + hex_color_g + hex_color_b
        cloth = ClothPng.objects.get(id=cloth_id)
        original_cloth_path = cloth.cloth_image
        changed_cloth_path = f'images/change_color_png'
        cloth_url_list = str(original_cloth_path).split('/')
        cloth_name = cloth_url_list[-1]
        changed_cloth_name = f'{color_hex}_{cloth_name}'
        os.makedirs(changed_cloth_path, exist_ok=True)

        def normalizer(x):  # rgb 값 0, 255 사이로 남을수있게 조절하기
            x = np.where(x > 255, 255, x)
            x = np.where(x < 5, 0, x)
            return x

        def colorswap(cloth_dir, res_dir, cloth_name, target_color):  # 색깔바꾸기 메인 함수
            s3 = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            original_cloth = Image.open(cloth_dir).convert("RGBA")
            np_original_cloth = np.array(original_cloth)
            backtorgb_image1 = cv2.cvtColor(np_original_cloth,cv2.COLOR_RGB2BGR)
            backtorgb_image = cv2.cvtColor(backtorgb_image1,cv2.COLOR_BGR2RGB)
            swap_image = backtorgb_image.astype(float)
            #그래이스케일 이미지 base value로 평준화 해주기
            swap_image = swap_image - get_base_value(backtorgb_image, 'mean')
            #크래이스케일이미지 색변환 해주기
            swap_image = normalizer(swap_image + target_color)
            #완성 이미지 1차 저장
            final_image = swap_image.astype(np.uint8)
            final_cloth_image = cv2.cvtColor(final_image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(res_dir + '/' + cloth_name, final_cloth_image)
            s3.upload_file(
                res_dir + '/' + cloth_name, AWS_STORAGE_BUCKET_NAME, 'media/' + res_dir + '/' + changed_cloth_name)

        # 관심지억 선언후 'mean','max', 또는 'min' 색깔 값 가져오기
        def get_base_value(original_image, return_type):
            #관심지억 선언하기
            roi = original_image[180:200, 240:260]
            roi_w, roi_h = roi.shape[:2]
            #3차원 배열 2차원으로 바꿔주기
            roi_reshape = np.reshape(roi, (roi_w * roi_h, 3))
            #배열의 sum구해서 max, min 색값의 index 찾고 저장하기
            roi_sum = np.sum(roi_reshape.astype(float), axis=1)
            roi_max = roi_reshape[np.argmax(roi_sum)]
            roi_min = roi_reshape[np.argmin(roi_sum)]
            #argument로 max, min, 또는 mean 선택할수있게 하기
            if return_type == 'mean':
                target_value = np.mean([roi_max, roi_min], axis=0)
            else:
                print('get_base_value: invalid target value')
            return target_value
        target_color = [color_r, color_g, color_b]
        colorswap(original_cloth_path, changed_cloth_path,
                  changed_cloth_name, target_color)
        changed_cloth_url = f'{MEDIA_URL}{changed_cloth_path}/{changed_cloth_name}'
        cloth_full_url = f'{MEDIA_URL}' + str(original_cloth_path)
        query = {}
        query['changed_cloth'] = changed_cloth_url
        query['cloth'] = cloth.id
        query['changed_color_r'] = color_r
        query['changed_color_g'] = color_g
        query['changed_color_b'] = color_b
        if not ChangedClothPng.objects.filter(changed_cloth=changed_cloth_url).exists():
            query_dict = QueryDict('', mutable=True)
            query_dict.update(query)
            serializer = ChangedClothPngSerializer(
                data=query_dict, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                context = {
                    'changed_cloth': changed_cloth_url,
                    'cloth': cloth_full_url,
                    'color': '##' + color_hex + f' (r, g, b)=({color_r}, {color_g}, {color_b})'
                }
                return Response(context, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response('Already exists Color Cloth', status=status.HTTP_400_BAD_REQUEST)
