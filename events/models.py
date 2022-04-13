from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.crypto import get_random_string


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

    capacity = models.IntegerField(blank=False)
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
        return self.participants.filter(created_at__date=self.window_end_date__date).count()


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


@receiver(post_save, sender=Booking)
def generate_booking_code(sender, instance, *args, **kwargs):
    """
    generate a booking code on pre_save signal
    """
    # it should only be generated if the booking code is not there
    if not instance.booking_code:
        # 5 digit random string to make it unique
        instance.booking_code = get_random_string(length=8)
        # TODO: scope for modification the booking code isn't really 100% unique
        # TODO: we can use uuid/ any suffix or prefix to make it unique
        instance.save()

