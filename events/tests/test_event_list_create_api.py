import random

from django.urls import resolve
from django.utils import timezone
from faker import Faker
from model_bakery import baker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from events.models import Event

fake = Faker()


class EventListCreateAPITestCase(APITestCase):
    """
    Test for the event list create API.
    """
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('events:events')

    def setUp(self):
        self.user = baker.make('accounts.CustomUser', is_staff=False, is_superuser=False)
        self.admin = baker.make('accounts.CustomUser', is_staff=True, is_superuser=True)

        self.payload = {
            'title': fake.text(max_nb_chars=50),
            'short_description': fake.text(max_nb_chars=100),
            'long_description': fake.text(),
            'start_date': timezone.now() + timezone.timedelta(days=10),
            'end_date': timezone.now() + timezone.timedelta(days=15),
            'window_start_date': timezone.now() + timezone.timedelta(days=1),
            'window_end_date': timezone.now() + timezone.timedelta(days=5),
            'capacity': random.randint(10, 100),
        }

    def test_url_resolves_to_event_list_create_view(self):
        view = resolve(self.url)
        self.assertEqual(view.func.view_class.__name__, 'EventListCreateAPIView')

    def test_event_create_api_unauthenticated_request_fails(self):
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_event_create_api_user_does_not_have_permission_to_create_event_fails(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_event_create_api_admin_can_create_event(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, self.payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # test few data
        self.assertEqual(response.data['title'], self.payload['title'])
        self.assertEqual(response.data['short_description'], self.payload['short_description'])

        # test organizer set to admin by default
        self.assertEqual(response.data['organizer'], self.admin.id)

        # test is_active set to True by default
        self.assertTrue(response.data['is_active'])

        # test Event db object created
        self.assertEqual(Event.objects.count(), 1)

    def test_absence_of_required_fields_causes_error(self):
        self.client.force_authenticate(user=self.admin)
        payload = self.payload.copy()
        payload.pop('title')
        payload.pop('short_description')

        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['title'][0], 'This field is required.')
        self.assertEqual(response.data['short_description'][0], 'This field is required.')

    def test_event_list_api_unauthenticated_request_fails(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_see_event_list(self):
        self.client.force_authenticate(user=self.admin)
        baker.make('events.Event', organizer=self.admin, _quantity=5)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_authenticated_user_can_see_registered_events(self):
        """
        Test that authenticated user can see only events he registered for
         if registered query param is set to True.
        """
        self.client.force_authenticate(user=self.admin)

        baker.make(
            'events.Event',
            _quantity=5,
            participants=[self.user],
            window_start_date=timezone.now() - timezone.timedelta(days=1),
            window_end_date=timezone.now() + timezone.timedelta(days=5)
        )
        baker.make(
            'events.Event',
            _quantity=5,
            window_start_date=timezone.now() - timezone.timedelta(days=1),
            window_end_date=timezone.now() + timezone.timedelta(days=5),
            start_date=timezone.now() + timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=15)
        )

        # authenticate the user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url + '?registered=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # should only show 5 events which s/he is registered for not the other 5
        self.assertEqual(len(response.data), 5)

    def test_authenticated_user_can_see_unregistered_events(self):
        """
        Test that authenticated user can see all events
         if registered query param is set to False or not sent.
        """
        self.client.force_authenticate(user=self.admin)

        baker.make(
            'events.Event',
            _quantity=5,
            participants=[self.user],
            window_start_date=timezone.now() - timezone.timedelta(days=1),
            window_end_date=timezone.now() + timezone.timedelta(days=5)
        )
        baker.make(
            'events.Event',
            _quantity=5,
            window_start_date=timezone.now() - timezone.timedelta(days=1),
            window_end_date=timezone.now() + timezone.timedelta(days=5),
            start_date=timezone.now() + timezone.timedelta(days=10),
            end_date=timezone.now() + timezone.timedelta(days=15)
        )

        # authenticate the user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url + '?registered=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # should see all events
        self.assertEqual(len(response.data), 10)















