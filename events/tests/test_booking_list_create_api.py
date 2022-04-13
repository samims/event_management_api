from model_bakery import baker
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from events.models import Event, Booking

User = get_user_model()


class BookingListCreateAPITestCase(APITestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.event = baker.make(
            Event,
            window_start_date=timezone.now() - timedelta(days=1),
            window_end_date=timezone.now() + timedelta(days=2),
            start_date=timezone.now() + timedelta(days=3),
            end_date=timezone.now() + timedelta(days=4),
        )

        self.url = reverse('events:bookings')
        self.data = {
            'event': self.event.id,
        }

    def test_create_booking_list_api_for_unauthenticated_user_fails(self):
        """
        Test that unauthenticated user cannot create a booking
        """
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_booking_list_create_for_authenticated_user_succeeds(self):
        """
        Test that authenticated user can create a booking
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_booking_create_api_for_authenticated_user_with_invalid_data_fails(self):
        """
        Test that authenticated user cannot create a booking with invalid data
        """
        self.client.force_authenticate(user=self.user)
        self.data['event'] = -1
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_booking_list_api_success(self):
        """
        Test that authenticated user can create a booking
        """
        self.client.force_authenticate(user=self.user)

        baker.make(Booking, event=self.event, participant=self.user, _quantity=4)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(
            list(Booking.objects.all().values_list('event', flat=True)),
            [self.event.id] * 4
        )
