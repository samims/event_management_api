import random

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from faker import Faker

from model_bakery import baker

from events.models import Event, Booking

fake = Faker()


class EventModelTest(TestCase):
    """
    Test the Event model
    """

    def setUp(self) -> None:
        self.user1 = baker.make('accounts.CustomUser', username='user1', email=fake.email())
        self.user2 = baker.make('accounts.CustomUser', username='user2', email=fake.email())
        self.user3 = baker.make('accounts.CustomUser', username='user3', email=fake.email())

        # Event data
        self.data_1 = {
            'start_date': timezone.now() + timezone.timedelta(days=10),
            'end_date': timezone.now() + timezone.timedelta(days=20),
            'window_start_date': timezone.now() + timezone.timedelta(days=5),
            'window_end_date': timezone.now() + timezone.timedelta(days=8),
            'capacity': random.randint(50, 100),
            'is_active': True,
        }

    def test_string_representation(self):
        event = Event(title=fake.text(20))
        self.assertEqual(str(event), event.title)

    def test_create_event_successful_with_proper_data(self):
        baker.make('events.Event', **self.data_1)
        self.assertEqual(Event.objects.count(), 1)

    def test_create_event_unsuccessful_with_invalid_data_raise(self):
        self.data_1['start_date'] = timezone.now() + timezone.timedelta(days=20)
        self.data_1['end_date'] = timezone.now() + timezone.timedelta(days=10)
        self.data_1['window_start_date'] = timezone.now() + timezone.timedelta(days=8)
        self.data_1['window_end_date'] = timezone.now() + timezone.timedelta(days=5)

        with self.assertRaises(ValidationError):
            baker.make('events.Event', **self.data_1)

        self.assertEqual(Event.objects.count(), 0)

    def test_no_of_participants(self):
        """
        Test the no of participants calculation property

        """
        self.data_1['participants'] = [self.user2, self.user3]
        self.data_1['window_start_date'] = timezone.now() - timezone.timedelta(days=5)
        self.data_1['window_end_date'] = timezone.now() + timezone.timedelta(days=5)
        self.data_1['organizer'] = self.user1

        event = baker.make('events.Event', **self.data_1)
        self.assertEqual(event.no_of_participants, 2)

    def test_remaining_set_count(self):
        """
        Test the remaining set count calculation property
        """
        self.data_1['participants'] = [self.user2, self.user3]
        self.data_1['organizer'] = self.user1
        self.data_1['window_start_date'] = timezone.now() - timezone.timedelta(days=5)
        self.data_1['window_end_date'] = timezone.now() + timezone.timedelta(days=5)

        event = baker.make('events.Event', **self.data_1)
        self.assertEqual(event.remaining_seat_count, event.capacity - event.no_of_participants)

    def test_is_open_for_booking(self):
        """
        Test the is_open_for_booking property
        """
        self.data_1['window_start_date'] = timezone.now() + timezone.timedelta(days=5)
        self.data_1['window_end_date'] = timezone.now() + timezone.timedelta(days=10)

        event = baker.make('events.Event', **self.data_1)

        # cause window_start_date and window_end_date both are in the future
        self.assertFalse(event.is_open_for_booking)

        # setting window_start_date in the past and window_end_date in the future
        # means that the event is open for booking
        self.data_1['window_start_date'] = timezone.now() - timezone.timedelta(days=1)
        self.data_1['window_end_date'] = timezone.now() + timezone.timedelta(days=1)

        event = baker.make('events.Event', **self.data_1)
        self.assertTrue(event.is_open_for_booking)

    def test_last_day_booked_seat_count(self):
        """
        Test the last day booked seat count property
        """
        self.data_1['organizer'] = self.user1
        self.data_1['window_start_date'] = timezone.now() - timezone.timedelta(days=1)
        self.data_1['window_end_date'] = timezone.now() + timezone.timedelta(days=1)
        event = baker.make('events.Event', **self.data_1)
        # create a booking for the event on today
        baker.make('events.Booking', event=event, participant=self.user2)

        self.assertEqual(event.last_day_booked_seat_count, 0)

        # setting today as the last day booked
        # and will be booking the event for the last day
        self.data_1['window_start_date'] = timezone.now() - timezone.timedelta(days=1)
        self.data_1['window_end_date'] = timezone.now() + timezone.timedelta(minutes=1)
        event = baker.make('events.Event', **self.data_1)

        # booking the event for the last day
        baker.make(
            'events.Booking',
            event=event,
            participant=self.user3,
        )
        self.assertEqual(event.last_day_booked_seat_count, 1)








