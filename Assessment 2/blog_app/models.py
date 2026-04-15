from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Q


class SpeciesQuerySet(models.QuerySet):
    def with_recording_stats(self):
        return self.annotate(
            recording_count=Count('recording', distinct=True),
            flagged_recording_count=Count('recording', filter=Q(recording__flagged=True), distinct=True),
        )


class SpeciesManager(models.Manager.from_queryset(SpeciesQuerySet)):
    pass

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

    objects = SpeciesManager()

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Recording(models.Model):
    class RecordingQuerySet(models.QuerySet):
        def with_related(self):
            return self.select_related('user', 'species', 'location').prefetch_related('anomaly_flags', 'anomaly_flags__flagged_by')

        def high_confidence(self, minimum_score=0.8):
            return self.filter(confidence_score__gte=minimum_score)

        def flagged_or_anomalous(self):
            return self.filter(Q(flagged=True) | Q(anomaly_flags__isnull=False)).distinct()

        def with_quality_metrics(self):
            return self.annotate(
                anomaly_count=Count('anomaly_flags', distinct=True),
                critical_anomaly_count=Count(
                    'anomaly_flags',
                    filter=Q(anomaly_flags__anomaly_type__in=['DISTORTION', 'MISSING_DATA']),
                    distinct=True,
                ),
            )

    class RecordingManager(models.Manager.from_queryset(RecordingQuerySet)):
        pass

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    audio_file = models.FileField(upload_to='recordings/')
    date_recorded = models.DateTimeField()

    confidence_score = models.FloatField()
    flagged = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = RecordingManager()

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