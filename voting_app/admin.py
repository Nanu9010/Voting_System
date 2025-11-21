# voting_app/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.db.models import Count
from .models import Candidate, Election, Vote, CandidacyApplication
from . import views_admin  # your admin views


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'start_date', 'end_date',
        'is_active', 'candidacy_registration_open', 'voting_open',
        'total_votes_display', 'results_link'
    ]
    list_editable = ['is_active', 'candidacy_registration_open', 'voting_open']
    list_filter = ['is_active', 'candidacy_registration_open', 'voting_open', 'start_date']
    search_fields = ['title']
    date_hierarchy = 'start_date'
    list_per_page = 50
    actions = ['open_candidacy', 'close_candidacy', 'open_voting', 'close_voting']

    # Pre-fetch vote count to avoid N+1
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_vote_count=Count('vote'))

    def total_votes_display(self, obj):
        return obj._vote_count
    total_votes_display.short_description = "Votes"
    total_votes_display.admin_order_field = '_vote_count'

    def results_link(self, obj):
        url = reverse('admin_election_results', args=[obj.id])
        return format_html('<a class="button" href="{}">Results</a>', url)
    results_link.short_description = ""

    # Bulk actions
    def open_candidacy(self, request, queryset):
        queryset.update(candidacy_registration_open=True)
    open_candidacy.short_description = "Open candidacy"

    def close_candidacy(self, request, queryset):
        queryset.update(candidacy_registration_open=False)
    close_candidacy.short_description = "Close candidacy"

    def open_voting(self, request, queryset):
        queryset.update(voting_open=True)
    open_voting.short_description = "Open voting"

    def close_voting(self, request, queryset):
        queryset.update(voting_open=False)
    close_voting.short_description = "Close voting"

    # Custom URL for results
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:election_id>/results/',
                self.admin_site.admin_view(views_admin.admin_election_results),
                name='admin_election_results'
            ),
        ]
        return custom_urls + urls


@admin.register(CandidacyApplication)
class CandidacyApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate_link', 'election_link', 'status', 'applied_at', 'approve_btn', 'reject_btn']
    list_filter = ['status', 'election', 'applied_at']
    search_fields = ['candidate__full_name', 'election__title']
    readonly_fields = ['applied_at', 'reviewed_at', 'reviewed_by']
    list_per_page = 50
    actions = None

    def candidate_link(self, obj):
        url = reverse("admin:voting_app_candidate_change", args=[obj.candidate.id])
        return format_html('<a href="{}">{}</a>', url, obj.candidate.full_name)
    candidate_link.short_description = "Candidate"

    def election_link(self, obj):
        url = reverse("admin:voting_app_election_change", args=[obj.election.id])
        return format_html('<a href="{}">{}</a>', url, obj.election.title)
    election_link.short_description = "Election"

    def approve_btn(self, obj):
        if obj.status == 'pending':
            url = reverse("admin_approve_candidacy", args=[obj.id])
            return format_html('<a class="button" href="{}">Approve</a>', url)
        return "Approved"
    approve_btn.short_description = ""

    def reject_btn(self, obj):
        if obj.status == 'pending':
            url = reverse("admin_reject_candidacy", args=[obj.id])
            return format_html('<a class="button" style="background:#c33" href="{}">Reject</a>', url)
        return "Rejected"
    reject_btn.short_description = ""


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'is_approved', 'applied_for_candidacy', 'vote_count']
    list_filter = ['is_approved', 'applied_for_candidacy']
    search_fields = ['full_name', 'email', 'ethereum_address']
    readonly_fields = ['vote_count', 'created_at']
    list_per_page = 50


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['election', 'voter', 'candidate', 'transaction_hash', 'voted_at']
    list_filter = ['election', 'voted_at']
    search_fields = ['transaction_hash', 'voter__full_name']
    readonly_fields = ['voted_at']
    list_per_page = 50