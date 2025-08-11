from django.db import models
from accounts.models import User

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2 ,null=True ,blank=True) 
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.symbol} - {self.name}"

class Alert(models.Model):
    ALERT_TYPES = (
        ('PRICE', 'Price Threshold'),
        ('DURATION', 'Duration'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPES)
    threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.email} - {self.stock.symbol} - {self.alert_type}"

class TriggeredAlert(models.Model):
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    triggered_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        ordering = ['-triggered_at']
    def __str__(self):
        return f"{self.alert} triggered at {self.triggered_at}"