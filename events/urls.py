from django.urls import path

from .views import (
    BookingListCreateAPIView,
    EventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
)


app_name = 'events'

urlpatterns = [
    path('', EventListCreateAPIView.as_view(), name='events'),
    path('/<int:pk>', EventRetrieveUpdateDestroyAPIView.as_view(), name='event'),
    path('/tickets', BookingListCreateAPIView.as_view(), name='bookings'),
]
