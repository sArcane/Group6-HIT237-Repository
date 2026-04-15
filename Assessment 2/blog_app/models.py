from django.db import models
from django.contrib.auth.models import User

class Species(models.Model):
    CONSERVATION_STATUS_CHOICES = [
        ('EX', 'Extinct'),
        ('EW', 'Extinct in the Wild'),
        ('CR', 'Critically Endangered'),
        ('EN', 'Endangered'),
        ('VU', 'Vulnerable'),
        ('NT', 'Near Threatened'),
        ('LC', 'Least Concern'),
        ('DD', 'Data Deficient'),
        ('NE', 'Not Evaluated'),
    ]

    name = models.CharField(max_length=200)
    scientific_name = models.CharField(max_length=200, blank=True)
    conservation_status = models.CharField(max_length=2, choices=CONSERVATION_STATUS_CHOICES, blank=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Recording(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    audio_file = models.FileField(upload_to='recordings/')
    date_recorded = models.DateTimeField()

    confidence_score = models.FloatField()
    flagged = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.species} - {self.date_recorded}"


class AnomalyFlag(models.Model):
    ANOMALY_TYPE_CHOICES = [
        ('NOISE', 'Excessive Noise'),
        ('DISTORTION', 'Audio Distortion'),
        ('MISSING_DATA', 'Missing Data'),
        ('ENVIRONMENTAL', 'Environmental Interference'),
        ('OTHER', 'Other'),
    ]

    recording = models.ForeignKey(Recording, on_delete=models.CASCADE, related_name='anomaly_flags')
    flagged_by = models.ForeignKey(User, on_delete=models.CASCADE)
    anomaly_type = models.CharField(max_length=20, choices=ANOMALY_TYPE_CHOICES)
    description = models.TextField(blank=True)
    flagged_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.anomaly_type} - {self.recording.id}"