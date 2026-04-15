from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.views import View

from .models import Recording, Species


class JSONResponseMixin:
	def render_json(self, payload, status=200):
		return JsonResponse(payload, status=status, safe=False)


class RecordingQuerysetMixin:
	def get_base_queryset(self):
		return Recording.objects.with_related().with_quality_metrics()


class RecordingListView(JSONResponseMixin, RecordingQuerysetMixin, View):
	def get(self, request):
		queryset = self.get_base_queryset().order_by('-date_recorded')

		min_confidence = request.GET.get('min_confidence')
		if min_confidence:
			try:
				queryset = queryset.high_confidence(float(min_confidence))
			except ValueError:
				return self.render_json({'error': 'min_confidence must be numeric'}, status=400)

		if request.GET.get('flagged_only') == 'true':
			queryset = queryset.flagged_or_anomalous()

		species_id = request.GET.get('species')
		if species_id:
			queryset = queryset.filter(species_id=species_id)

		data = [
			{
				'id': recording.id,
				'species': recording.species.name,
				'location': recording.location.name,
				'recorded_by': recording.user.username,
				'date_recorded': recording.date_recorded.isoformat(),
				'confidence_score': recording.confidence_score,
				'flagged': recording.flagged,
				'anomaly_count': recording.anomaly_count,
				'critical_anomaly_count': recording.critical_anomaly_count,
			}
			for recording in queryset
		]

		return self.render_json({'count': len(data), 'results': data})


class RecordingDetailView(JSONResponseMixin, RecordingQuerysetMixin, View):
	def get(self, request, pk):
		recording = self.get_base_queryset().filter(pk=pk).first()
		if not recording:
			return self.render_json({'error': 'Recording not found'}, status=404)

		return self.render_json(
			{
				'id': recording.id,
				'species': {
					'name': recording.species.name,
					'scientific_name': recording.species.scientific_name,
					'conservation_status': recording.species.conservation_status,
				},
				'location': recording.location.name,
				'recorded_by': recording.user.username,
				'date_recorded': recording.date_recorded.isoformat(),
				'confidence_score': recording.confidence_score,
				'flagged': recording.flagged,
				'anomaly_count': recording.anomaly_count,
				'critical_anomaly_count': recording.critical_anomaly_count,
				'anomalies': [
					{
						'id': anomaly.id,
						'anomaly_type': anomaly.anomaly_type,
						'description': anomaly.description,
						'flagged_by': anomaly.flagged_by.username,
						'flagged_at': anomaly.flagged_at.isoformat(),
					}
					for anomaly in recording.anomaly_flags.all()
				],
			}
		)


class SpeciesAnalyticsView(JSONResponseMixin, View):
	def get(self, request):
		species_rankings = (
			Species.objects.with_recording_stats()
			.filter(recording_count__gt=0)
			.values('id', 'name', 'scientific_name', 'recording_count', 'flagged_recording_count')
			.order_by('-recording_count', 'name')
		)

		recording_totals = Recording.objects.aggregate(
			total_recordings=Count('id'),
			avg_confidence=Avg('confidence_score'),
			flagged_count=Count('id', filter=Q(flagged=True)),
		)

		return self.render_json(
			{
				'summary': {
					'total_recordings': recording_totals['total_recordings'],
					'avg_confidence': recording_totals['avg_confidence'],
					'flagged_count': recording_totals['flagged_count'],
				},
				'species_rankings': list(species_rankings),
			}
		)
