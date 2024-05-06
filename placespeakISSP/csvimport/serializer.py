from rest_framework import serializers
from .models import *

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
    
class CSVUploadSerializer(serializers.Serializer):
    csv_data = serializers.CharField(required=True, allow_blank=False)

    def validate_csv_data(self, value):
        # Validate CSV data as needed
        if not value:
            raise serializers.ValidationError("CSV data cannot be empty.")
        # You can also add custom CSV validation here
        return value
        
