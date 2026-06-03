from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AISettingViewSet

router = DefaultRouter()
router.register(r"settings", AISettingViewSet, basename="ai-setting")

urlpatterns = [
    path("", include(router.urls)),
]
