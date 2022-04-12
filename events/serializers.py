from rest_framework import serializers

from .models import Event, Booking


class EventListSerializer(serializers.ModelSerializer):
    """
    Serializer for Event List View
    """

    class Meta:
        model = Event
        exclude = ('created_at', 'updated_at', 'participants')


class EventCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for Event Create View
    """
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = Event
        fields = '__all__'

    def validate(self, data):
        """
        Validate the data
        """
        # check if the user is admin
        if not self.context['request'].user.is_superuser:
            raise serializers.ValidationError(
                'Only admin can create events')

        # set the owner of the event to the current user
        data['organizer'] = self.context['request'].user
        return data


class EventRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for Event Retrieve View
    """

    class Meta:
        model = Event
        fields = '__all__'

    def to_representation(self, instance):
        """
        Override to_representation to modify the output/response
        """
        data = super(EventRetrieveSerializer, self).to_representation(instance)
        # we should show details of participants in public list api
        # for admin it's ok
        if not self.context['request'].user.is_superuser:
            data.pop('participants')
        return data


class EventUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for Event Update View
    """

    class Meta:
        model = Event
        fields = '__all__'


class BookingListSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking List View
    """
    class Meta:
        model = Booking
        fields = '__all__'


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking Create View
    """
    participant = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Booking
        fields = '__all__'


class BookingRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for Booking Retrieve View
    """

    class Meta:
        model = Booking
        fields = '__all__'


