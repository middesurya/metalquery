"""
Chatbot Serializers
DRF serializers for API endpoints.
"""
from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat request."""
    question = serializers.CharField(max_length=1000, required=True)
    mode = serializers.ChoiceField(
        choices=['auto', 'nlp-sql', 'rag'],
        default='auto',
        required=False
    )
    user_id = serializers.CharField(max_length=100, required=False)
    organization_id = serializers.CharField(max_length=100, required=False)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat response."""
    success = serializers.BooleanField()
    query_type = serializers.CharField()
    response = serializers.CharField(allow_null=True)
    sql = serializers.CharField(allow_null=True)
    results = serializers.ListField(child=serializers.DictField(), allow_null=True)
    sources = serializers.ListField(child=serializers.CharField(), allow_null=True)
    row_count = serializers.IntegerField()
    error = serializers.CharField(allow_null=True, required=False)


class DualQueryRequestSerializer(serializers.Serializer):
    """Serializer for dual query endpoint."""
    question = serializers.CharField(max_length=1000, required=True)
    mode = serializers.ChoiceField(
        choices=['nlp-sql', 'rag', 'auto'],
        default='auto',
        help_text="Force query mode or auto-detect"
    )


class DualQueryResponseSerializer(serializers.Serializer):
    """Serializer for dual query response."""
    success = serializers.BooleanField()
    query_type = serializers.CharField()
    response = serializers.CharField(allow_null=True)
    sql = serializers.CharField(allow_null=True, required=False)
    results = serializers.ListField(
        child=serializers.DictField(),
        allow_null=True,
        required=False
    )
    sources = serializers.ListField(
        child=serializers.CharField(),
        allow_null=True,
        required=False
    )
    row_count = serializers.IntegerField(required=False)
    routing_confidence = serializers.FloatField(required=False)
    error = serializers.CharField(allow_null=True, required=False)


class SchemaTableSerializer(serializers.Serializer):
    """Serializer for table schema."""
    name = serializers.CharField()
    type = serializers.CharField()
    description = serializers.CharField(required=False)
    foreign_key = serializers.CharField(required=False)


class SchemaResponseSerializer(serializers.Serializer):
    """Serializer for schema response."""
    success = serializers.BooleanField()
    schema = serializers.DictField()
    source = serializers.CharField()


class HealthResponseSerializer(serializers.Serializer):
    """Serializer for health check response."""
    status = serializers.CharField()
    service = serializers.CharField()
    version = serializers.CharField()
    components = serializers.DictField()
