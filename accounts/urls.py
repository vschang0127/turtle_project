from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path("register/", Registration.as_view(), name='registration_api'),
    path("login/", Login.as_view(), name='login_api'),
    ]
