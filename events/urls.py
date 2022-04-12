from django.urls import path

from .views import EventListCreateAPIView, EventRetrieveUpdateDestroyAPIView


app_name = 'events'

urlpatterns = [
    path('', EventListCreateAPIView.as_view(), name='event_list_create'),
    path('/<int:pk>', EventRetrieveUpdateDestroyAPIView.as_view(), name='event_detail'),
]
