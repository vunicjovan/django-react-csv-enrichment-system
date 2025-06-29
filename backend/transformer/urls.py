from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .base.health import HealthCheckView
from .files.views import FileUploadViewSet

# API Router
router = DefaultRouter()
router.register(r"files", FileUploadViewSet, basename="file")

# URL patterns
urlpatterns = [
    path("api/", include(router.urls)),
    path("health", HealthCheckView.as_view(), name="health_check"),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
