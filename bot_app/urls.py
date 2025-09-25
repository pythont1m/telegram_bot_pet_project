from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('api/', include('tg_bot.urls')),
    path('admin/', admin.site.urls),


]

