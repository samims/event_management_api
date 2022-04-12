from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser

from .models import Event
from events.serializers import (
    EventListSerializer,
    EventCreateSerializer,
    EventRetrieveSerializer,
    EventUpdateSerializer
)


class EventListCreateAPIView(ListCreateAPIView):
    """
    List all events, or create a new event.
    """
    serializer_class = EventListSerializer
    queryset = Event.objects.order_by('-start_date')
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        """
        Override the default serializer class
        to return the appropriate serializer class for request method.
        """
        if self.request.method == 'GET':
            return EventListSerializer
        return EventCreateSerializer

    def get_permissions(self):
        """
        Override the default permission class
        to allow only admin users to create events.
        """
        if self.request.method == 'GET':
            return [IsAuthenticatedOrReadOnly()]
        return [IsAdminUser()]

    def perform_create(self, serializer):
        """
        Override the default create method to
        set the user that created the event.
        """
        serializer.save(organizer=self.request.user)


class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a event instance.
    """
    queryset = Event.objects.all()

    def get_serializer_class(self):
        """
        Override the default serializer class
        to return the appropriate serializer class for request method.
        """
        if self.request.method == 'GET':
            return EventRetrieveSerializer
        return EventUpdateSerializer

    def get_permissions(self):
        """
        Override the default permission class
        to allow only admin users to update events.
        """
        if self.request.method == 'GET':
            return [IsAuthenticatedOrReadOnly()]
        return [IsAdminUser()]
