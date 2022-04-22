from django.urls import path
from .views import *

app_name = 'fitting'

urlpatterns = [
    path('upload_user_photo/', MyPhotoViewSet.as_view({'get': 'show_list', 'post':'create', 'delete':'delete'})),
    path('my_prefer_cloth/', MyPreferClothViewSet.as_view({'get': 'show_list', 'post':'create', 'delete':'delete'})),
    path('fit_test/', FittingViewSet.as_view({'get':'show_list'}))
]
