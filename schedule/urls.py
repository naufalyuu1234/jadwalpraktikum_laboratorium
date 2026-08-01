from django.urls import path

from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.schedule_list, name='list'),
    path('add/', views.schedule_create, name='create'),
    path('<int:schedule_id>/', views.schedule_detail, name='detail'),
    path('<int:schedule_id>/book/', views.book_practicum, name='book'),
]