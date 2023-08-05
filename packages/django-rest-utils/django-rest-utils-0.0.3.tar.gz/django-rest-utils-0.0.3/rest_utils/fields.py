from rest_framework import serializers


class FlexRelatedField(serializers.PrimaryKeyRelatedField):
    """
    This serialize users PrimaryKeyRelatedField field for deserialization
    and the provided serializer for serialization.
    """
    def __init__(self, *args, **kwargs):
        self.serializer_class = kwargs.pop('serializer_class')
        self.kwargs = kwargs
        super(FlexRelatedField, self).__init__(*args, **kwargs)

    def to_native(self, value):
        native = self.from_native(value)
        return self.serializer_class(native).data
