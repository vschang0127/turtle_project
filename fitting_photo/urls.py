from django.urls import path
from .views import *


app_name = 'fitting_photo'

urlpatterns = [
    path('fitting_my_photo/', MyFittingClothViewSet.as_view({'get':'show_list', 'post':'create'})),
]
