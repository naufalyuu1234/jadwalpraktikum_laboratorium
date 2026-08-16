from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.api_schedule_list, name='api_schedule_list')
]