from rest_framework import serializers
from .models import PanicEvent

class PanicEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PanicEvent
        fields = ['id', 'user', 'latitude', 'longitude', 'timestamp', 'status']
        read_only_fields = ['user', 'timestamp', 'status']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
