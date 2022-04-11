from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Event
from events.serializers import EventListSerializer


class EventListCreateAPIView(ListAPIView):
    """
    List all events, or create a new event.
    """
    serializer_class = EventListSerializer
    queryset = Event.objects.order_by('-start_date')
    permission_classes = (IsAuthenticatedOrReadOnly,)

