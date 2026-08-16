from django.urls import include, path

from . import views

app_name = 'schedule'

urlpatterns = [
    path('', views.schedule_list, name='list'),
    path('add/', views.schedule_create, name='create'),
    path('<int:schedule_id>/', views.schedule_detail, name='detail'),
    path('<int:schedule_id>/refresh-participants/', views.schedule_refresh_participants, name='refresh_participants'),
    path('<int:schedule_id>/hard-wipe/', views.schedule_hard_wipe, name='hard_wipe'),
    path('<int:schedule_id>/book/', views.book_practicum, name='book'),

    # API endpoints
    path('api/', include('schedule.api.urls')),
]