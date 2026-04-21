from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    priority = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return f"{self.name} - {self.phone_number}"
