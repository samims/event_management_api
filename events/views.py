from rest_framework.exceptions import NotFound
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response

from core.permissions import IsAdminOrOwnerOnly
from .models import Event, Booking
from events.serializers import (
    BookingListSerializer,
    BookingCreateSerializer,
    EventListSerializer,
    EventCreateSerializer,
    EventRetrieveSerializer,
    EventUpdateSerializer, BookingRetrieveSerializer, EventSummarySerializer
)


class EventListCreateAPIView(ListCreateAPIView):
    """
    List all events, or create a new event.
    """
    serializer_class = EventListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        qs = Event.objects.all()
        is_registered = self.request.query_params.get('registered', '').lower()
        if is_registered == 'true':
            qs = qs.filter(participants__in=[self.request.user])
        return qs.order_by('-start_date')

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
            return [IsAuthenticated()]
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


class BookingListCreateAPIView(ListCreateAPIView):
    """
    List all bookings, or create a new booking.
    """
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        """
        Override the default queryset method
        to return the bookings for the current user.
        """
        return Booking.objects.filter(participant=self.request.user)

    def get_serializer_class(self):
        """
        Override the default serializer class
        to return the appropriate serializer class for request method.
        """
        if self.request.method == 'GET':
            return BookingListSerializer
        return BookingCreateSerializer


class BookingRetrieveAPIView(RetrieveAPIView):
    """
    Retrieve a booking instance.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingRetrieveSerializer
    permission_classes = (IsAdminOrOwnerOnly,)


class EventSummaryAPIView(GenericAPIView):
    """
    Retrieve a summary of events.
    """
    queryset = Event.objects.all()
    serializer_class = EventSummarySerializer
    permission_classes = (IsAdminUser, )

    def get(self, request, *args, **kwargs):

        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def get_object(self):
        qs = self.filter_queryset(self.queryset)
        try:
            obj = qs.get(pk=self.kwargs.get('pk'))
        except Event.DoesNotExist:
            raise NotFound('Event not found')
        return obj




