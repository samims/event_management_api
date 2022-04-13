from django.contrib.auth import get_user_model
from django.utils import timezone
from model_bakery import baker
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from events.models import Event, Booking


class BookingRetrieveAPITestCase(APITestCase):
    def setUp(self):
        self.event = baker.make(
            Event,
            window_start_date=timezone.now() - timezone.timedelta(days=1),
            window_end_date=timezone.now() + timezone.timedelta(days=1),
            start_date=timezone.now() + timezone.timedelta(days=4),
            end_date=timezone.now() + timezone.timedelta(days=5),

        )

        self.user = baker.make(get_user_model())
        self.url = reverse('events:booking', kwargs={'pk': self.event.id})

    def test_booking_retrieve_api_success(self):
        """
        Test that a user is allowed to retrieve a booking if they are authenticated
        """
        baker.make(
            Booking,
            event=self.event,
            participant=self.user
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url, {'event': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_booking_retrieve_available_for_booked_user_but_not_for_others(self):
        """
        Test that a user is allowed to retrieve a booking if they are authenticated
        """
        baker.make(
            Booking,
            event=self.event,
            participant=self.user
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url, {'event': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_2 = baker.make(get_user_model())
        self.client.force_authenticate(user=user_2)
        response = self.client.get(self.url, {'event': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)




