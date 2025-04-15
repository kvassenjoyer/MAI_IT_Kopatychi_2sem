from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
import Events.views

urlpatterns = [
    path('', Events.views.render_home, name='home'),
    path('admin/', admin.site.urls),
    path('users/', include('Events.urls')),
    path('users/', include('django.contrib.auth.urls')),
]
