from django import forms
from .models import Create_vote

class EditVoteForm(forms.ModelForm):
    class Meta:
        model = Create_vote
        fields = ['nameVote', 'description', 'imageVote']
