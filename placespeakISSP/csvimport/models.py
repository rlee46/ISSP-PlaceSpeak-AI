# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
# csvimport/models.py

from django.db import models
class Report(models.Model):
    question = models.TextField()
    contribution = models.TextField()
    status = models.CharField(max_length=100)
    sentiment = models.CharField(max_length=100)
    confidence_score = models.CharField(max_length=100)
    date_submitted = models.DateTimeField()

    def __unicode__(self):
        return self.question

# class Discussion(models.Model):
#     id = models.AutoField(primary_key=True)
#     reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
#     title = models.CharField(max_length=255)
#     content = models.TextField()
#     creation = models.DateTimeField()
#     display_name = models.CharField(max_length=255)
#     polygon_label = models.CharField(max_length=255, blank=True, null=True)
#     up_votes = models.IntegerField(default=0)
#     down_votes = models.IntegerField(default=0)
#     discussion_type = models.CharField(max_length=100)
#     anonymous = models.BooleanField(default=False)
#     deleted = models.BooleanField(default=False)
#     is_moderated = models.BooleanField(default=False)
#     author = models.CharField(max_length=255, blank=True, null=True)
    
#     def __str__(self):
#         return self.title
    
# class SurveyResponse(models.Model):
#     response_id = models.CharField(max_length=50)
#     date_submitted = models.DateTimeField()
#     last_page = models.IntegerField()
#     start_language = models.CharField(max_length=10)
#     token = models.CharField(max_length=100)
#     date_started = models.DateTimeField()
#     date_last_action = models.DateTimeField()
#     homeowner_resident = models.BooleanField(default=False)
#     business_owner = models.BooleanField(default=False)
#     prefer_not_to_disclose = models.BooleanField(default=False)
#     institution = models.BooleanField(default=False)
#     ward_1 = models.BooleanField(default=False)
#     ward_2 = models.BooleanField(default=False)
#     ward_3 = models.BooleanField(default=False)
#     ward_4 = models.BooleanField(default=False)
#     ward_5 = models.BooleanField(default=False)
#     unsure_ward = models.BooleanField(default=False)
#     noise_increased = models.BooleanField(default=False)
#     noise_stayed_same = models.BooleanField(default=False)
#     noise_unsure = models.BooleanField(default=False)
#     noise_decreased = models.BooleanField(default=False)
#     experience_domestic_noise = models.BooleanField(default=False)
#     experience_loud_music = models.BooleanField(default=False)
#     experience_dogs_barking = models.BooleanField(default=False)
#     experience_construction_noise = models.BooleanField(default=False)
#     experience_deliveries_pickup = models.BooleanField(default=False)
#     experience_commercial_noise = models.BooleanField(default=False)
#     experience_other_noise = models.BooleanField(default=False)
#     bylaw_more_restrictive = models.BooleanField(default=False)
#     bylaw_about_same = models.BooleanField(default=False)
#     bylaw_less_restrictive = models.BooleanField(default=False)
#     bylaw_unsure = models.BooleanField(default=False)
#     grant_temporary_exemptions = models.BooleanField(default=False)
#     in_favor_of_noise_fee = models.BooleanField(default=False)
#     fee_waived_for_nonprofit_yes = models.BooleanField(default=False)
#     fee_waived_for_nonprofit_no = models.BooleanField(default=False)
#     fee_waived_for_nonprofit_unsure = models.BooleanField(default=False)
#     more_restrictive_conditions_yes = models.BooleanField(default=False)
#     more_restrictive_conditions_no = models.BooleanField(default=False)
#     more_restrictive_conditions_unsure = models.BooleanField(default=False)
#     change_permitted_times_yes = models.BooleanField(default=False)
#     change_permitted_times_no = models.BooleanField(default=False)
#     change_permitted_times_unsure = models.BooleanField(default=False)
#     additional_bylaw_considerations = models.TextField(blank=True, null=True)
#     polygon = models.CharField(max_length=255, blank=True, null=True)
#     user_id = models.CharField(max_length=50)
    
#     # Optional: You can add __str__ method to display the object in a readable format
#     def __str__(self):
#         return f"Response {self.response_id}"