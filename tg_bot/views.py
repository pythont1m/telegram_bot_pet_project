from rest_framework.decorators import api_view
from rest_framework.response import Response
from bot_project.flights.models import Flight, SearchHistory
from bot_project.users.models import TelegramUser
from .serializers import FlightSerializer, SearchHistorySerializer

@api_view(['GET'])
def flight_list(request):
    from_city = request.GET.get('from')
    to_city = request.GET.get('to')
    date = request.GET.get('date')

    flights = Flight.objects.all()
    if from_city:
        flights = flights.filter(departure_city__iexact=from_city)
    if to_city:
        flights = flights.filter(arrival_city__iexact=to_city)
    if date:
        flights = flights.filter(date=date)

    serializer = FlightSerializer(flights, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def save_search(request):
    serializer = SearchHistorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'status': 'ok'})
    return Response(serializer.errors, status=400)
