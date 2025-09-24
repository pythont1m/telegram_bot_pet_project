from rest_framework import serializers
from bot_project.flights.models import Flight, SearchHistory
from bot_project.users.models import TelegramUser

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = '__all__'
