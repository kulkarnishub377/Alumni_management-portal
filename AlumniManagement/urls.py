from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from alumni import views

urlpatterns = [
    path('', include('alumni.urls')),  # Include your app's URLs first
    path('admin/', admin.site.urls),  # Admin URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
