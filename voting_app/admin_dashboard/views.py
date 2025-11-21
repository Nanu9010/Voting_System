# voting_app/admin_dashboard/views.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count
from django.http import HttpResponse
import csv

from ..models import Election, CandidacyApplication, Candidate, AdminActionLog


class StaffOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


def _log(user, action, election=None, details=""):
    AdminActionLog.objects.create(user=user, action=action, election=election, details=details)


class AdminDashboardView(StaffOnlyMixin, TemplateView):
    template_name = "admin_dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        elections = (Election.objects
                     .annotate(vote_count=Count('vote'))
                     .order_by('-start_date'))
        ctx['elections'] = elections
        ctx['pending_apps'] = (CandidacyApplication.objects
                               .filter(status='pending')
                               .select_related('candidate', 'election')[:30])
        ctx['recent_logs'] = AdminActionLog.objects.select_related('user', 'election')[:15]
        return ctx


# ----------------------------------------------------------------------
# AJAX HANDLERS (the ones that were missing)
# ----------------------------------------------------------------------
def toggle_field(request, election_id, field):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    election = get_object_or_404(Election, id=election_id)
    allowed = ['is_active', 'candidacy_registration_open', 'voting_open']
    if field not in allowed:
        return JsonResponse({"error": "invalid field"}, status=400)

    new_val = request.POST.get('value') == 'true'
    setattr(election, field, new_val)
    election.save(update_fields=[field])

    _log(request.user, f"Toggle {field}", election, f"{field} → {new_val}")
    return JsonResponse({"status": "ok", "value": new_val})


def approve_candidacy(request, app_id):
    app = get_object_or_404(CandidacyApplication, id=app_id, status='pending')
    with transaction.atomic():
        app.status = 'approved'
        app.reviewed_by = request.user
        app.reviewed_at = timezone.now()
        app.save()
        app.candidate.is_approved = True
        app.candidate.save()
        _log(request.user, "Approve candidacy", app.election, app.candidate.full_name)
    return JsonResponse({"status": "ok"})


def reject_candidacy(request, app_id):
    app = get_object_or_404(CandidacyApplication, id=app_id, status='pending')
    with transaction.atomic():
        app.status = 'rejected'
        app.reviewed_by = request.user
        app.reviewed_at = timezone.now()
        app.save()
        _log(request.user, "Reject candidacy", app.election, app.candidate.full_name)
    return JsonResponse({"status": "ok"})


def force_end_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    with transaction.atomic():
        election.is_active = False
        election.voting_open = False
        election.save(update_fields=['is_active', 'voting_open'])
        _log(request.user, "Force-end election", election)
    return JsonResponse({"status": "ok"})


# ----------------------------------------------------------------------
# CSV EXPORT (secure – only staff, only approved candidates)
# ----------------------------------------------------------------------
def export_csv(request, election_id):
    if not request.user.is_staff:
        return HttpResponse("Forbidden", status=403)

    election = get_object_or_404(Election, id=election_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{election.title}_results.csv"'

    writer = csv.writer(response)
    writer.writerow(['Candidate', 'Votes'])

    for c in Candidate.objects.filter(is_approved=True, votes_received__election=election):
        writer.writerow([c.full_name, c.vote_count])

    return response