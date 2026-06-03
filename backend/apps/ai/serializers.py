from rest_framework import serializers

from .models import AISetting


class AISettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AISetting
        fields = ["id", "provider", "model", "temperature", "max_tokens", "is_active", "updated_at"]
