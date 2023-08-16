from django import forms
from .models import Create_vote
from django.forms import DateTimeInput




class EditVoteForm(forms.ModelForm):
    class Meta:
        model = Create_vote
        fields = ['nameVote', 'description', 'imageVote']


class CreateVoteForm(forms.ModelForm):
    class Meta:
        model = Create_vote
        fields = ['closingVote']  # Agrega otros campos según sea necesario
        widgets = {
            'closingVote': DateTimeInput(attrs={'type': 'datetime-local'}),
        }
