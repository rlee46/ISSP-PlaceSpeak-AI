from rest_framework import serializers
from .models import *

class CSVUploadSerializer(serializers.Serializer):
    csv_data = serializers.CharField(required=True, allow_blank=False)
    
class EntrySerializer(serializers.Serializer):
    KeyPhrases = serializers.CharField()
    Sentiment = serializers.CharField()
    ReactionEmotion = serializers.CharField()
    ConfidenceScore = serializers.CharField()
    Location = serializers.CharField()
    
class AnalysisDataSerializer(serializers.Serializer):
    summary = serializers.CharField(allow_blank=True)
    entries = EntrySerializer(many=True)
    confidence_frequencies = serializers.ListField(child=serializers.IntegerField())
    sentiment_frequencies = serializers.DictField(child=serializers.IntegerField())
