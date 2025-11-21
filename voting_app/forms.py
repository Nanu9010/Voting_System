from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Candidate, CandidacyApplication

class CandidateRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=200, required=True)
    age = forms.IntegerField(min_value=18, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    photo = forms.ImageField(required=False)
    manifesto = forms.CharField(widget=forms.Textarea, required=True)
    ethereum_address = forms.CharField(max_length=42, required=True, label="Ethereum Wallet Address")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            candidate = Candidate.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                age=self.cleaned_data['age'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address'],
                photo=self.cleaned_data.get('photo'),
                manifesto=self.cleaned_data['manifesto'],
                ethereum_address=self.cleaned_data['ethereum_address']
            )
        return user

class CandidateUpdateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['full_name', 'age', 'email', 'phone', 'address', 'photo', 'manifesto']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'manifesto': forms.Textarea(attrs={'rows': 4}),
        }

class CandidacyApplicationForm(forms.ModelForm):
    class Meta:
        model = CandidacyApplication
        fields = ['application_text']
        widgets = {
            'application_text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Explain why you want to stand for election and what you hope to achieve...'
            }),
        }
        labels = {
            'application_text': 'Application Statement'
        }