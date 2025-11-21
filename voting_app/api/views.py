# voting_app/api/views.py
from django.http import JsonResponse
from django.db.models import Count
from ..models import Candidate  # ← ..models because we're inside api/

def election_results_json(request, election_id):
    qs = (Candidate.objects
          .filter(is_approved=True, votes_received__election_id=election_id)
          .annotate(v=Count('votes_received'))
          .values('full_name', 'v'))
    return JsonResponse({
        'labels': [x['full_name'] for x in qs],
        'votes':  [x['v'] for x in qs]
    })