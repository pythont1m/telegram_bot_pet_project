from django.db import models
from users.models import TelegramUser

class Flight(models.Model):
    flight_id = models.CharField(max_length=50)
    departure_city = models.CharField(max_length=50)
    arrival_city = models.CharField(max_length=50)
    date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

class SearchHistory(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    from_city = models.CharField(max_length=50)
    to_city = models.CharField(max_length=50)
    date = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)
