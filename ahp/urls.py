from django.urls import path, include
from ahp.views import *

app_name = 'ahp'

urlpatterns = [
    path('', ahp, name='ahp'),
    path('bobot-aktif/', bobot_aktif, name='bobot_aktif'),
    path('bobot-history/', bobot_history, name='bobot_history'),
    path('biodata/', biodata, name='biodata'),
    path('edit-biodata/', edit_biodata, name='edit_biodata'),
    path('proses-ranking/', proses_ranking, name='proses_ranking'),
    path('buka-beasiswa/', buka_beasiswa, name='buka_beasiswa'),
]