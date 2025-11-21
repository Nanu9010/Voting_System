# voting_app/admin_dashboard/views_ajax.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_staff)
@require_POST
def toggle_field(request, election_id, field):
    election = get_object_or_404(Election, id=election_id)
    allowed = ['is_active', 'candidacy_registration_open', 'voting_open']
    if field not in allowed:
        return JsonResponse({'error': 'invalid'}, status=400)

    new_val = request.POST.get('value') == 'true'
    setattr(election, field, new_val)
    election.save(update_fields=[field])

    _log(request.user, f"Toggle {field}", election, f"→ {new_val}")
    return JsonResponse({'status': 'ok', 'value': new_val})


@user_passes_test(lambda u: u.is_staff)
@require_POST
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
    return JsonResponse({'status': 'ok'})


@user_passes_test(lambda u: u.is_staff)
@require_POST
def reject_candidacy(request, app_id):
    app = get_object_or_404(CandidacyApplication, id=app_id, status='pending')
    with transaction.atomic():
        app.status = 'rejected'
        app.reviewed_by = request.user
        app.reviewed_at = timezone.now()
        app.save()
        _log(request.user, "Reject candidacy", app.election, app.candidate.full_name)
    return JsonResponse({'status': 'ok'})


@user_passes_test(lambda u: u.is_staff)
@require_POST
def force_end_election(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    with transaction.atomic():
        election.is_active = False
        election.voting_open = False
        election.save(update_fields=['is_active', 'voting_open'])
        _log(request.user, "Force-end election", election)
    return JsonResponse({'status': 'ok'})