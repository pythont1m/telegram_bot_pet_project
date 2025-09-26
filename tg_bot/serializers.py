from rest_framework import serializers
from users.models import TelegramUser
from flights.models import Flight, SearchHistory

class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ['telegram_id', 'username']

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'

class SearchHistorySerializer(serializers.ModelSerializer):
    user = TelegramUserSerializer(read_only=True)

    class Meta:
        model = SearchHistory
        fields = ['id', 'user', 'from_city', 'to_city', 'date', 'timestamp']
