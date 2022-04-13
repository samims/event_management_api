from django.contrib.auth import get_user_model
from django.utils import timezone
from model_bakery import baker
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class EventSummaryAPITestCase(APITestCase):
    def setUp(self):
        self.user = baker.make(get_user_model(), is_staff=False, is_superuser=False)
        self.admin_user = baker.make(get_user_model(), is_staff=True, is_superuser=True)

        self.event = baker.make(
            'events.Event',
            window_start_date=timezone.now() - timezone.timedelta(days=1),
            window_end_date=timezone.now() + timezone.timedelta(days=1),
            start_date=timezone.now() - timezone.timedelta(days=1),
            end_date=timezone.now() + timezone.timedelta(days=1),
            organizer=self.admin_user
        )
        self.event_summary_url = reverse('events:summary', args=[self.event.pk])

    def test_event_summary_api_fails_without_authentication(self):
        """
        Test that the request fails without authentication.
        """
        response = self.client.get(self.event_summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_request_fails_for_user_role(self):
        """
        Test that the request fails for user role.
        as it's only relevant for admin users.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.event_summary_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_event_summary_api_succeeds_for_admin_user(self):
        """
        Test that the request succeeds for admin user.
        """
        self.client.force_authenticate(user=self.admin_user)
        user_list = baker.make(get_user_model(), _quantity=10)
        self.event.participants.add(*user_list)



        response = self.client.get(self.event_summary_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['id'], self.event.pk)
        self.assertEqual(response.data['title'], self.event.title)
        self.assertEqual(response.data['short_description'], self.event.short_description)
        self.assertEqual(response.data['long_description'], self.event.long_description)
        self.assertEqual(response.data['start_date'], self.event.start_date.isoformat())
        self.assertEqual(response.data['end_date'], self.event.end_date.isoformat())
        self.assertEqual(response.data['window_start_date'], self.event.window_start_date.isoformat())
        self.assertEqual(response.data['window_end_date'], self.event.window_end_date.isoformat())
        self.assertEqual(response.data['is_active'], self.event.is_active)
        self.assertEqual(response.data['organizer'], self.event.organizer.pk)
        self.assertEqual(response.data['participants'], [user.pk for user in self.event.participants.all()])
        self.assertEqual(response.data['no_of_participants'], self.event.no_of_participants)
