from django.urls import path

from .views import (
    BookingListCreateAPIView,
    BookingRetrieveAPIView,
    EventListCreateAPIView,
    EventRetrieveUpdateDestroyAPIView,
)


app_name = 'events'

urlpatterns = [
    path('', EventListCreateAPIView.as_view(), name='events'),
    path('/<int:pk>', EventRetrieveUpdateDestroyAPIView.as_view(), name='event'),
    path('/tickets', BookingListCreateAPIView.as_view(), name='bookings'),
    path('/tickets/<int:pk>', BookingRetrieveAPIView.as_view(), name='booking'),
]
