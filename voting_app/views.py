from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Candidate, Election, Vote, CandidacyApplication
from .forms import CandidateRegistrationForm, CandidateUpdateForm, CandidacyApplicationForm
from datetime import datetime
import json

# ... rest of your views code ...

def home(request):
    elections = Election.objects.filter(is_active=True)
    return render(request, 'home.html', {'elections': elections})

def register(request):
    if request.method == 'POST':
        form = CandidateRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to the voting system.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CandidateRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard(request):
    try:
        candidate = request.user.candidate
        active_elections = Election.objects.filter(is_active=True)
        pending_applications = CandidacyApplication.objects.filter(
            candidate=candidate, 
            status='pending'
        )
        
        context = {
            'candidate': candidate,
            'elections': active_elections,
            'pending_applications': pending_applications
        }
        return render(request, 'dashboard.html', context)
    except Candidate.DoesNotExist:
        messages.error(request, 'Candidate profile not found.')
        return redirect('home')

@login_required
def update_profile(request):
    candidate = request.user.candidate
    if request.method == 'POST':
        form = CandidateUpdateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CandidateUpdateForm(instance=candidate)
    
    return render(request, 'update_profile.html', {'form': form, 'candidate': candidate})

@login_required
def apply_for_candidacy(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidate = request.user.candidate
    
    # Check if already applied
    existing_application = CandidacyApplication.objects.filter(
        candidate=candidate, 
        election=election
    ).first()
    
    if existing_application:
        messages.warning(request, f'You have already applied for {election.title}')
        return redirect('dashboard')
    
    if not election.candidacy_registration_open:
        messages.error(request, 'Candidacy registration is closed for this election.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CandidacyApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.candidate = candidate
            application.election = election
            application.save()
            
            # Mark candidate as applied
            candidate.applied_for_candidacy = True
            candidate.save()
            
            messages.success(request, 'Your candidacy application has been submitted for admin approval!')
            return redirect('dashboard')
    else:
        form = CandidacyApplicationForm()
    
    return render(request, 'apply_candidacy.html', {
        'form': form,
        'election': election,
        'candidate': candidate
    })

@login_required
def election_detail(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    # Only show approved candidates
    candidates = Candidate.objects.filter(is_approved=True)
    candidate = request.user.candidate
    
    has_voted = Vote.objects.filter(election=election, voter=candidate).exists()
    is_voting_time = election.is_voting_time() and election.voting_open
    
    # Check if user has pending application for this election
    has_pending_application = CandidacyApplication.objects.filter(
        candidate=candidate,
        election=election,
        status='pending'
    ).exists()
    
    context = {
        'election': election,
        'candidates': candidates,
        'has_voted': has_voted,
        'is_voting_time': is_voting_time,
        'current_candidate': candidate,
        'has_pending_application': has_pending_application
    }
    return render(request, 'election_detail.html', context)

@login_required
@csrf_exempt
def record_vote(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            election_id = data.get('election_id')
            candidate_id = data.get('candidate_id')
            transaction_hash = data.get('transaction_hash')
            
            election = get_object_or_404(Election, id=election_id)
            candidate = get_object_or_404(Candidate, id=candidate_id, is_approved=True)
            voter = request.user.candidate
            
            # Check if already voted
            if Vote.objects.filter(election=election, voter=voter).exists():
                return JsonResponse({'success': False, 'error': 'You have already voted in this election.'})
            
            # Check voting time and if voting is open
            if not election.is_voting_time() or not election.voting_open:
                return JsonResponse({'success': False, 'error': 'Voting is not open at this time.'})
            
            # Record vote
            vote = Vote.objects.create(
                election=election,
                voter=voter,
                candidate=candidate,
                transaction_hash=transaction_hash
            )
            
            # Update vote count
            candidate.vote_count += 1
            candidate.save()
            
            # Mark voter as having voted
            voter.has_voted = True
            voter.save()
            
            return JsonResponse({'success': True, 'message': 'Vote recorded successfully!'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

@login_required
def results(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidates = Candidate.objects.filter(is_approved=True).order_by('-vote_count')
    total_votes = sum(c.vote_count for c in candidates)
    
    context = {
        'election': election,
        'candidates': candidates,
        'total_votes': total_votes
    }
    return render(request, 'results.html', context)

# Admin Views
@staff_member_required
def admin_candidacy_applications(request):
    pending_applications = CandidacyApplication.objects.filter(status='pending').select_related('candidate', 'election')
    approved_applications = CandidacyApplication.objects.filter(status='approved').select_related('candidate', 'election')
    rejected_applications = CandidacyApplication.objects.filter(status='rejected').select_related('candidate', 'election')
    
    context = {
        'pending_applications': pending_applications,
        'approved_applications': approved_applications,
        'rejected_applications': rejected_applications,
    }
    return render(request, 'admin/candidacy_applications.html', context)

@staff_member_required
def approve_candidacy(request, application_id):
    application = get_object_or_404(CandidacyApplication, id=application_id)
    
    if request.method == 'POST':
        application.status = 'approved'
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.review_notes = request.POST.get('review_notes', '')
        application.save()
        
        # Approve the candidate
        candidate = application.candidate
        candidate.is_approved = True
        candidate.save()
        
        messages.success(request, f'Candidacy application for {candidate.full_name} has been approved.')
    
    return redirect('admin_candidacy_applications')

@staff_member_required
def reject_candidacy(request, application_id):
    application = get_object_or_404(CandidacyApplication, id=application_id)
    
    if request.method == 'POST':
        application.status = 'rejected'
        application.reviewed_by = request.user
        application.reviewed_at = timezone.now()
        application.review_notes = request.POST.get('review_notes', '')
        application.save()
        
        messages.warning(request, f'Candidacy application for {application.candidate.full_name} has been rejected.')
    
    return redirect('admin_candidacy_applications')