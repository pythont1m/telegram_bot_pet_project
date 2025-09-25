from rest_framework.decorators import api_view
from rest_framework.response import Response
from flights.models import Flight, SearchHistory
from users.models import TelegramUser
from .serializers import FlightSerializer, SearchHistorySerializer
from amadeus import Client
import os

amadeus_client = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET")
)

@api_view(['GET'])
def flight_list(request):
    from_city = request.GET.get('from')
    to_city = request.GET.get('to')
    date = request.GET.get('date')

    if not (from_city and to_city and date):
        return Response({"error": "from, to, and date are required"}, status=400)

    try:
        response = amadeus_client.shopping.flight_offers_search.get(
            originLocationCode=from_city,
            destinationLocationCode=to_city,
            departureDate=date,
            adults=1
        )
        data = response.data
        return Response(data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def save_search(request):
    serializer = SearchHistorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'status': 'ok'})
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def search_history(request):
    user_id = request.GET.get('user_id')
    if not user_id:
        return Response({"error": "user_id required"}, status=400)
    try:
        history = SearchHistory.objects.filter(user__telegram_id=user_id).order_by('-timestamp')
        serializer = SearchHistorySerializer(history, many=True)
        return Response(serializer.data)
    except TelegramUser.DoesNotExist:
        return Response([], status=200)
