# voting_app/admin_dashboard/urls.py  (NO CHANGE NEEDED — but ensure name='admin_dashboard')
from django.urls import path
from . import views

urlpatterns = [
    path('', views.AdminDashboardView.as_view(), name='admin_dashboard'),  # ← /dashboard/admin/

    path('toggle/<int:election_id>/<str:field>/', views.toggle_field, name='admin_toggle_field'),
    path('approve/<int:app_id>/', views.approve_candidacy, name='admin_approve_candidacy'),
    path('reject/<int:app_id>/', views.reject_candidacy, name='admin_reject_candidacy'),
    path('force-end/<int:election_id>/', views.force_end_election, name='admin_force_end'),
    path('export/<int:election_id>/', views.export_csv, name='admin_export_csv'),
]