# device/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.device_status, name='device_status'),
    path('control_led/<str:state>/', views.control_led, name='control_led'),
    path('status/', views.device_status, name='device_status'),
    path('latest-data/', views.latest_data_view, name='latest_data'),
]
