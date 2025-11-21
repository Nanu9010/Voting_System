# voting_app/urls.py  (APP — MOVE DASHBOARD OUT)
from django.urls import path, include
from . import views, views_admin

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('election/<int:election_id>/', views.election_detail, name='election_detail'),
    path('election/<int:election_id>/apply/', views.apply_for_candidacy, name='apply_candidacy'),
    path('record-vote/', views.record_vote, name='record_vote'),
    path('results/<int:election_id>/', views.results, name='results'),

    # ADMIN DASHBOARD — MOVED TO /dashboard/admin/
    path('dashboard/admin/', include('voting_app.admin_dashboard.urls')),

    # Legacy (keep, but rename if conflicting)
    path('dashboard/admin/approve-candidacy/<int:app_id>/', views_admin.admin_approve_candidacy, name='admin_approve_candidacy'),
    path('dashboard/admin/reject-candidacy/<int:app_id>/', views_admin.admin_reject_candidacy, name='admin_reject_candidacy'),
    path('dashboard/admin/election/<int:election_id>/results/', views_admin.admin_election_results, name='admin_election_results'),
]