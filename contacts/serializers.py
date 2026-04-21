from rest_framework import serializers
from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone_number', 'priority']

    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            return attrs
            
        user = request.user
        contacts_count = user.contacts.count()
        
        # Only validate on create
        if not self.instance:
            if user.tier == 'free' and contacts_count >= 3:
                raise serializers.ValidationError("Los usuarios gratuitos pueden tener un máximo de 3 contactos.")
            elif user.tier == 'premium' and contacts_count >= 10:
                raise serializers.ValidationError("Has alcanzado el límite máximo de 10 contactos para usuarios premium.")
                
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
