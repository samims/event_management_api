from faker import Faker
from model_bakery import baker
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse, resolve

from events.models import Event


fake = Faker()


class EventRetrieveUpdateDestroyAPITestCase(APITestCase):
    def setUp(self):
        # create a user
        self.user = baker.make(
            get_user_model(),
            is_staff=False,
            is_superuser=False
        )
        # Create an admin user
        self.admin = baker.make(
            get_user_model(),
            is_staff=True,
            is_superuser=False
        )
        # Create an event
        self.event = baker.make(
            Event,
            window_start_date=timezone.now() - timezone.timedelta(days=1),
            window_end_date=timezone.now() + timezone.timedelta(days=1),
            start_date=timezone.now() + timezone.timedelta(days=5),
            end_date=timezone.now() + timezone.timedelta(days=10),
        )

        self.payload = {
            'title': fake.text(max_nb_chars=50),
            'short_description': self.event.short_description,
            'long_description': self.event.long_description,
            'window_start_date': self.event.window_start_date,
            'window_end_date': self.event.window_end_date,
            'start_date': self.event.start_date,
            'end_date': self.event.end_date,
            'capacity': 5,
            'organizer': self.event.organizer.id,
        }

        self.url = reverse('events:event', args=[self.event.id])

    def test_retrieve_event_api_unauthenticated_request_fails(self):
        """
        Test that an unauthenticated request fails and returns a 401
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_event_api_authenticated_request_succeeds(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.event.id)
        self.assertEqual(response.data['title'], self.event.title)

    def test_update_event_api_unauthenticated_request_fails(self):
        """
        Test that an unauthenticated update request fails and returns a 401
        """
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_event_api_authenticated_user_role_request_fails(self):
        """
        Test that an authenticated user with a role other than admin fails
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_event_api_authenticated_admin_request_succeeds(self):
        """
        Test that an authenticated admin request succeeds
        """
        self.client.force_authenticate(user=self.admin)
        new_title = fake.text(max_nb_chars=50)
        self.payload['title'] = new_title
        response = self.client.put(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.event.id)

        self.event.refresh_from_db()
        # Check that the event has been updated in the database
        self.assertEqual(self.event.title, new_title)

    def test_destroy_event_api_unauthenticated_request_fails(self):
        """
        Test that an unauthenticated destroy request fails and returns a 401
        """
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_destroy_event_api_authenticated_user_role_request_fails(self):
        """
        Test that an authenticated user with a role other than admin fails
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_event_api_authenticated_admin_request_succeeds(self):
        """
        Test that an authenticated admin request succeeds
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())
