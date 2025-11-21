# voting_app/views_admin.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils import timezone
from .models import CandidacyApplication, Election, Candidate


@staff_member_required
def admin_approve_candidacy(request, app_id):
    app = get_object_or_404(CandidacyApplication, id=app_id)
    if app.status != "pending":
        messages.error(request, "Already processed.")
    else:
        app.status = "approved"
        app.reviewed_by = request.user
        app.reviewed_at = timezone.now()
        app.save()
        app.candidate.is_approved = True
        app.candidate.save()
        messages.success(request, f"{app.candidate.full_name} approved.")
    return redirect("admin:voting_app_candidacyapplication_changelist")


@staff_member_required
def admin_reject_candidacy(request, app_id):
    app = get_object_or_404(CandidacyApplication, id=app_id)
    if app.status != "pending":
        messages.error(request, "Already processed.")
    else:
        app.status = "rejected"
        app.reviewed_by = request.user
        app.reviewed_at = timezone.now()
        app.save()
        messages.warning(request, f"{app.candidate.full_name} rejected.")
    return redirect("admin:voting_app_candidacyapplication_changelist")


@staff_member_required
def admin_election_results(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidates = Candidate.objects.filter(is_approved=True).order_by('-vote_count')
    total = sum(c.vote_count for c in candidates)
    return render(request, "admin/election_results.html", {
        "election": election,
        "candidates": candidates,
        "total": total,
    })

def force_end_election(self, request, queryset):
    updated = queryset.update(is_active=False, voting_open=False)
    self.message_user(request, f"{updated} election(s) force-ended by {request.user}.", level='warning')
force_end_election.short_description = "Force End Election"