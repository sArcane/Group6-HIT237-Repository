from datetime import timedelta
from tempfile import TemporaryDirectory

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AnomalyFlag, Location, Recording, Species


class MediaIsolatedTestCase(TestCase):
	def setUp(self):
		super().setUp()
		self._temp_media = TemporaryDirectory()
		self._settings_context = self.settings(MEDIA_ROOT=self._temp_media.name)
		self._settings_context.enable()

	def tearDown(self):
		self._settings_context.disable()
		self._temp_media.cleanup()
		super().tearDown()


class RecordingQuerysetTests(MediaIsolatedTestCase):
	def setUp(self):
		super().setUp()
		self.user = User.objects.create_user(username='tester', password='pass12345')
		self.flagger = User.objects.create_user(username='reviewer', password='pass12345')
		self.species = Species.objects.create(name='Magpie', scientific_name='Gymnorhina tibicen', conservation_status='LC')
		self.location = Location.objects.create(name='Darwin Wetlands')

		self.recording = Recording.objects.create(
			user=self.user,
			species=self.species,
			location=self.location,
			audio_file=SimpleUploadedFile('bird.wav', b'audio-bytes', content_type='audio/wav'),
			date_recorded=timezone.now() - timedelta(days=1),
			confidence_score=0.92,
			flagged=True,
		)
		AnomalyFlag.objects.create(
			recording=self.recording,
			flagged_by=self.flagger,
			anomaly_type='DISTORTION',
			description='Clipping detected in first 5 seconds',
		)

	def test_with_quality_metrics_annotates_counts(self):
		row = Recording.objects.with_quality_metrics().get(pk=self.recording.pk)
		self.assertEqual(row.anomaly_count, 1)
		self.assertEqual(row.critical_anomaly_count, 1)

	def test_flagged_or_anomalous_returns_expected_recordings(self):
		ids = set(Recording.objects.flagged_or_anomalous().values_list('id', flat=True))
		self.assertIn(self.recording.id, ids)


class RecordingViewTests(MediaIsolatedTestCase):
	def setUp(self):
		super().setUp()
		self.user = User.objects.create_user(username='observer', password='pass12345')
		self.flagger = User.objects.create_user(username='qa_user', password='pass12345')

		self.magpie = Species.objects.create(name='Magpie', scientific_name='Gymnorhina tibicen', conservation_status='LC')
		self.owl = Species.objects.create(name='Barn Owl', scientific_name='Tyto alba', conservation_status='LC')
		self.location = Location.objects.create(name='Campus Reserve')

		self.recording_1 = Recording.objects.create(
			user=self.user,
			species=self.magpie,
			location=self.location,
			audio_file=SimpleUploadedFile('magpie.wav', b'audio-1', content_type='audio/wav'),
			date_recorded=timezone.now() - timedelta(hours=2),
			confidence_score=0.95,
			flagged=True,
		)
		self.recording_2 = Recording.objects.create(
			user=self.user,
			species=self.owl,
			location=self.location,
			audio_file=SimpleUploadedFile('owl.wav', b'audio-2', content_type='audio/wav'),
			date_recorded=timezone.now() - timedelta(hours=1),
			confidence_score=0.62,
			flagged=False,
		)

		AnomalyFlag.objects.create(
			recording=self.recording_1,
			flagged_by=self.flagger,
			anomaly_type='DISTORTION',
			description='Noticeable clipping in waveform.',
		)

	def test_recording_list_view_supports_filters(self):
		response = self.client.get(reverse('blog_app:recording-list'), {'min_confidence': '0.8', 'flagged_only': 'true'})
		self.assertEqual(response.status_code, 200)

		payload = response.json()
		self.assertEqual(payload['count'], 1)
		self.assertEqual(payload['results'][0]['id'], self.recording_1.id)

	def test_recording_detail_view_returns_anomalies(self):
		response = self.client.get(reverse('blog_app:recording-detail', kwargs={'pk': self.recording_1.id}))
		self.assertEqual(response.status_code, 200)

		payload = response.json()
		self.assertEqual(payload['id'], self.recording_1.id)
		self.assertEqual(payload['species']['name'], 'Magpie')
		self.assertEqual(len(payload['anomalies']), 1)

	def test_species_analytics_returns_aggregates(self):
		response = self.client.get(reverse('blog_app:species-analytics'))
		self.assertEqual(response.status_code, 200)

		payload = response.json()
		self.assertEqual(payload['summary']['total_recordings'], 2)
		self.assertEqual(payload['summary']['flagged_count'], 1)
		self.assertGreaterEqual(len(payload['species_rankings']), 2)