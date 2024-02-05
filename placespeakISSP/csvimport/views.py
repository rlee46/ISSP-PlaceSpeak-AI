# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from .forms import CSVUploadForm
from .models import SurveyResponse
import csv

def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            for row in reader:
                SurveyResponse.objects.create(
                    response_id=row['Response ID'],
                    date_submitted=row['2. Date submitted'],
                    last_page=row['3. Last page'],
                    # ... continue mapping each CSV column to the model fields
                )
            # Add some success message or redirect
        else:
            # Add some error message or handling
            pass
    else:
        form = CSVUploadForm()
    return render(request, 'csvimport/upload_csv.html', {'form': form})