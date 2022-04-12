from django.contrib import admin

from .models import Event, Booking


#
class CustomBookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'event', 'participant',
        'booking_code', 'created_at'
    )


admin.site.register(Event)
admin.site.register(Booking, CustomBookingAdmin)
