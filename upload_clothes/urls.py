from django.urls import path
from .views import *

app_name = 'upload_clothes'

urlpatterns = [
    path('cloth_list/', cloth_list, name='cloth_list'),
    path('cloth_total/', cloth_total, name='cloth_total'),
    path('change_color/', ChangedClothViewSet.as_view({'get': 'show_list', 'post':'change_color'})),
    path('change_color_png/', ChangedClothPngViewSet.as_view({'get': 'show_list', 'post':'change_color'})),

]
