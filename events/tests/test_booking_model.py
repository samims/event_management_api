from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from events.models import Booking


class BookingModelTest(TestCase):
    """
    Test the Booking model
    """
    def setUp(self) -> None:
        self.user1 = baker.make('accounts.CustomUser', username='user1')
        self.user2 = baker.make('accounts.CustomUser', username='user2')
        self.event = baker.make(
            'events.Event',
            window_start_date=timezone.now() - timedelta(days=1),
            window_end_date=timezone.now() + timedelta(days=1),
        )

    def test_booking_is_created_successfully(self):
        """
        Test that a booking is created successfully
        """
        booking = baker.make('events.Booking', participant=self.user1, event=self.event)
        self.event.window_start_date = timezone.now() - timedelta(days=1)
        self.event.window_end_date = timezone.now() + timedelta(days=1)
        self.event.save()

        self.assertEqual(Booking.objects.count(), 1)
        self.assertEqual(booking.participant, self.user1)
        self.assertEqual(booking.event, self.event)

    def test_booking_is_not_possible_for_closed_window_event(self):
        """
        Test that a booking is not possible for a closed window event
        """
        self.event.window_start_date = timezone.now() - timedelta(days=5)
        self.event.window_end_date = timezone.now() - timedelta(days=4)

        self.event.save()

        with self.assertRaises(ValidationError):
            baker.make('events.Booking', participant=self.user1, event=self.event)

    def test_booking_code_is_generated(self):
        """
        Test that a booking code is generated
        """
        booking = baker.make('events.Booking', participant=self.user1, event=self.event)
        self.assertTrue(booking.booking_code)

