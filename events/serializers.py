from rest_framework import serializers

from .models import Event


class EventListSerializer(serializers.ModelSerializer):
    """
    Serializer for Event List View
    """
    class Meta:
        model = Event
        fields = '__all__'

    def to_representation(self, instance):
        """
        Override to_representation to modify the output/response
        """
        data = super(EventListSerializer, self).to_representation(instance)
        # we should show details of participants in public list api
        if not self.context['request'].user.is_superuser:
            data.pop('participants')
        return data


