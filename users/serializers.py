from rest_framework import serializers
from .models import CustomUser
from roles.models import Role
from roles.serializers import RoleSerializer

class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(), 
        many=True, 
        write_only=True, 
        source='roles',
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone_number', 'tier', 'is_active', 'is_staff', 'is_superuser', 'roles', 'role_ids']
