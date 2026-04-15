from django import forms
from .models import Recording, Species, Location


class RecordingForm(forms.ModelForm):
    class Meta:
        model = Recording
        fields = ['species', 'location', 'audio_file', 'date_recorded', 'confidence_score']
        widgets = {
            'species': forms.Select(attrs={
                'class': 'form-select form-control',
                'required': 'required'
            }),
            'location': forms.Select(attrs={
                'class': 'form-select form-control',
                'required': 'required'
            }),
            'audio_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*',
                'required': 'required'
            }),
            'date_recorded': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': 'required'
            }),
            'confidence_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '0',
                'max': '1',
                'step': '0.01',
                'required': 'required',
                'placeholder': '0.00 - 1.00'
            }),
        }
        labels = {
            'species': 'Species',
            'location': 'Location',
            'audio_file': 'Audio File (MP3, WAV, etc.)',
            'date_recorded': 'Date & Time Recorded',
            'confidence_score': 'Confidence Score (0.0 - 1.0)',
        }
