# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import math
import os
from django.shortcuts import render,redirect

from rest_framework.views import APIView
from . models import *
from rest_framework.response import Response
from . serializer import *
from django.http import QueryDict

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from tests.test_confidence import test_confidence
from tests.test_sentiment import test_sentiment
from collections import defaultdict
import requests
import csv
import re
import time
import json

from services.csv_processing import DataProcessorFactory


class CSVAnalysisView(APIView):
    def post(self, request):
        # Parse the form-encoded data
        form_data = QueryDict(request.body)
        json_string = form_data.get('_content')

        if not json_string:
            return Response({'error': 'Missing JSON data'}, status=400)

        try:
            # Decode and load JSON data
            data = json.loads(json_string)

        except json.JSONDecodeError as e:
            return Response({'error': 'Invalid JSON: ' + str(e)}, status=400)
        
        factory = DataProcessorFactory()
        try:
            #if not provided, will fall back to discussion
            data_type = data.get("data_type", "discussion")
            processor = factory.get_processor(data_type)
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        
        print(data.get('csv_data'))
        serializer = CSVUploadSerializer(data=data)
        if serializer.is_valid():
            csv_data = serializer.validated_data['csv_data']
        else:
            return Response(serializer.errors, status=400)
        analysis = processor.generate_analysis(csv_data)
        return analysis
        









