from rest_framework import permissions, viewsets

from .models import AISetting
from .serializers import AISettingSerializer


class AISettingViewSet(viewsets.ModelViewSet):
    queryset = AISetting.objects.all().order_by("-updated_at")
    serializer_class = AISettingSerializer
    permission_classes = [permissions.IsAdminUser]
