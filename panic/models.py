from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PanicEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='panic_events')
    latitude = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=8, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Triggered')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Panic Event by {self.user.email} at {self.timestamp}"
