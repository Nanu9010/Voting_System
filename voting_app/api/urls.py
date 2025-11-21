# voting_app/api/urls.py
from django.urls import path
from . import views   # ← this is voting_app/api/views.py

urlpatterns = [
    path('election-results/<int:election_id>/', views.election_results_json),
]