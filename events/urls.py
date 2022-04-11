from django.urls import path

from .views import EventListCreateAPIView


app_name = 'events'

urlpatterns = [
    path('', EventListCreateAPIView.as_view(), name='event_list_create'),
]
