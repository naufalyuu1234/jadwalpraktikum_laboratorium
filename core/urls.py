from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('accounts/', include('authentication.urls')),
    path('admin/', admin.site.urls),
    path('schedule/', include('schedule.urls')),
]
