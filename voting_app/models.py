from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import date

class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    age = models.IntegerField(validators=[MinValueValidator(18)])
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    photo = models.ImageField(upload_to='candidates/', blank=True, null=True)
    manifesto = models.TextField(help_text="Your election manifesto")
    
    # Admin approval system
    is_approved = models.BooleanField(default=False, help_text="Admin approved to stand for election")
    applied_for_candidacy = models.BooleanField(default=False, help_text="User has applied to stand for election")
    
    ethereum_address = models.CharField(max_length=42, unique=True, blank=True, null=True)
    vote_count = models.IntegerField(default=0)
    has_voted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.full_name
    
    @property
    def is_standing(self):
        return self.is_approved and self.applied_for_candidacy
    
    class Meta:
        ordering = ['-vote_count']

class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    voting_start_time = models.TimeField(default='09:00:00')
    voting_end_time = models.TimeField(default='17:00:00')
    is_active = models.BooleanField(default=True)
    blockchain_contract_address = models.CharField(max_length=42, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Admin settings
    candidacy_registration_open = models.BooleanField(default=True, help_text="Whether candidates can apply for election")
    voting_open = models.BooleanField(default=True, help_text="Whether voting is open")
    
    def __str__(self):
        return self.title
    
    
    def is_voting_time(self):
        from datetime import datetime
        now = datetime.now()
        today = now.date()
        current_time = now.time()
        
        if self.start_date <= today <= self.end_date:
            if self.voting_start_time <= current_time <= self.voting_end_time:
                return True
        return False
    
    def total_votes(self):
        return Vote.objects.filter(election=self).count()
    total_votes.short_description = "Votes"

class Vote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    voter = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes_cast')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes_received')
    transaction_hash = models.CharField(max_length=66, unique=True)
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('election', 'voter')
    
    def __str__(self):
        return f"{self.voter.full_name} voted for {self.candidate.full_name}"

class CandidacyApplication(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    application_text = models.TextField(help_text="Why you want to stand for election")
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('candidate', 'election')
    
    def __str__(self):
        return f"{self.candidate.full_name} - {self.election.title}"
    




    # voting_app/models.py (add at bottom)

class AdminActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    election = models.ForeignKey(Election, null=True, blank=True, on_delete=models.SET_NULL)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Admin Action"
        verbose_name_plural = "Admin Actions"

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"