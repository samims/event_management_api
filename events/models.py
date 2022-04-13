import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.crypto import get_random_string

from accounts.models import CustomUser

logger = logging.getLogger(__name__)


class BaseModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Event(BaseModel):
    """
    Event model holds all the info about events
    """
    title = models.CharField(max_length=255, blank=False, db_index=True)
    short_description = models.CharField(max_length=255, blank=False)
    long_description = models.TextField(blank=True, default='')
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(db_index=True)

    window_start_date = models.DateTimeField(db_index=True)
    window_end_date = models.DateTimeField(db_index=True)

    capacity = models.PositiveIntegerField(blank=False)
    is_active = models.BooleanField(default=True)
    participants = models.ManyToManyField(get_user_model(), through='Booking',
                                          related_name='participated_events')

    # the person who created the event
    organizer = models.ForeignKey(get_user_model(), related_name='events',
                                  on_delete=models.CASCADE)

    class Meta:
        ordering = ['-start_date']
        get_latest_by = 'start_date'

    def __str__(self):
        return self.title

    def clean(self):
        """
        Validate the email field to make sure it is a valid email address.
        for some weird reason, django does not validate the email field on creation
        """
        # validate start_date and end_date
        if self.start_date > self.end_date:
            raise ValidationError('Start date cannot be after end date')

        # validate window_start_date and window_end_date
        if self.window_start_date > self.window_end_date:
            raise ValidationError('Window start date cannot be after window end date')

        super(Event, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        return super(Event, self).save(*args, **kwargs)

    @property
    def no_of_participants(self):
        """
        Returns the number of participants for the event
        """
        return self.participants.count()

    @property
    def remaining_seat_count(self):
        """
        Returns the remaining seat count
        """
        return self.capacity - self.no_of_participants

    @property
    def is_open_for_booking(self):
        """
        Returns True if the event is open for booking
        """

        is_booking_window_available = self.window_start_date <= timezone.now() <= self.window_end_date
        is_seat_available = bool(self.remaining_seat_count)
        # both conditions should be true to open for booking
        return is_booking_window_available and is_seat_available

    @property
    def last_day_booked_seat_count(self):
        """
        Returns the last day booked seat count
        """
        last_day_booking_qs = Booking.objects.filter(
            created_at__day=self.window_end_date.day,
            created_at__month=self.window_end_date.month,
            created_at__year=self.window_end_date.year,
            event=self
        )
        return last_day_booking_qs.count()


class Booking(BaseModel):
    """
    Booking model is and intermediate model between Event and User aka participants
    we can use this for through relation

    purpose of this model is to store extra info about the booking like
    creation date, payment status, etc if needed
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    booking_code = models.CharField(max_length=255, blank=True, db_index=True)

    def __str__(self):
        return self.booking_code

    class Meta:
        ordering = ('-created_at',)
        get_latest_by = 'created_at'

    @property
    def booked_at(self):
        """
        property to get the booking date which is an al
        """
        return self.created_at

    @property
    def owner(self):
        """
        property to get the owner of the booking
        Doing this to reuse the permission class where we generally
        user obj.owner == request.user & here owner == participant
        """
        return self.participant

    @property
    def is_booking_window_open(self):
        """
        Returns True if the booking window is open
        """
        return self.event.window_start_date <= timezone.now() <= self.event.window_end_date


@receiver(post_save, sender=Booking)
def generate_booking_code(sender, instance, *args, **kwargs):
    """
    generate a booking code on pre_save signal
    Making this post_save instead of pre_save to make sure that at least the obj is saved in db
    booking code even can be generated manually
    """
    # it should only be generated if the booking code is not there
    if not instance.booking_code:
        # 5 digit random string to make it unique
        instance.booking_code = get_random_string(length=8)
        # TODO: scope for modification the booking code isn't really 100% unique
        # TODO: we can use uuid/ any suffix or prefix to make it unique
        instance.save()


@receiver(pre_save, sender=Booking)
def pre_save_handler(sender, instance, *args, **kwargs):
    if not instance.is_booking_window_open:
        logger.warning('Booking window is closed for event: %s', instance.event.id)
        raise ValidationError('Booking window is closed')
