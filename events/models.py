from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
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


class Booking(BaseModel):
    """
    Booking model is and intermediate model between Event and User aka participants
    we can use this for through relation

    purpose of this model is to store extra info about the booking like
    creation date, payment status, etc if needed
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    booking_code = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return self.booking_code

    class Meta:
        ordering = ('-created_at',)
        get_latest_by = 'created_at'
