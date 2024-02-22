from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^download-data/$', views.download_data, name='download_data'),
    url(r'^send-csv-to-api/$', views.send_csv_to_api, name='send_csv_to_api'),
]