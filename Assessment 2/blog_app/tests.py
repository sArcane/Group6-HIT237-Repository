from datetime import timedelta
from tempfile import TemporaryDirectory

from django.contrib.auth.models import AnonymousUser, Permission, User
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AnomalyFlag, Location, Recording, Species
from .services import flag_recording, review_recording, submit_recording


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
		self.client.force_login(self.user)

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
		review_perm = Permission.objects.get(codename='review_recordings')
		self.user.user_permissions.add(review_perm)

		response = self.client.get(reverse('blog_app:recording-list'), {'min_confidence': '0.8', 'flagged_only': 'true'})
		self.assertEqual(response.status_code, 200)

		recordings = list(response.context['recordings'])
		self.assertEqual(len(recordings), 1)
		self.assertEqual(recordings[0].id, self.recording_1.id)

	def test_recording_detail_view_returns_anomalies(self):
		response = self.client.get(reverse('blog_app:recording-detail', kwargs={'pk': self.recording_1.id}))
		self.assertEqual(response.status_code, 200)

		recording = response.context['recording']
		self.assertEqual(recording.id, self.recording_1.id)
		self.assertEqual(recording.species.name, 'Magpie')
		self.assertEqual(recording.anomaly_flags.count(), 1)

	def test_species_analytics_returns_aggregates(self):
		analytics_perm = Permission.objects.get(codename='view_species_analytics')
		self.user.user_permissions.add(analytics_perm)

		response = self.client.get(reverse('blog_app:species-analytics'))
		self.assertEqual(response.status_code, 200)

		summary = response.context['summary']
		species_rankings = list(response.context['species_rankings'])
		self.assertEqual(summary['total_recordings'], 2)
		self.assertEqual(summary['flagged_count'], 1)
		self.assertGreaterEqual(len(species_rankings), 2)


class ServiceTests(MediaIsolatedTestCase):
	def setUp(self):
		super().setUp()
		self.user = User.objects.create_user(username='submitter', password='pass12345')
		self.reviewer = User.objects.create_user(username='reviewer2', password='pass12345')
		review_perm = Permission.objects.get(codename='review_recordings')
		self.reviewer.user_permissions.add(review_perm)

		self.species = Species.objects.create(
			name='Kookaburra', scientific_name='Dacelo novaeguineae', conservation_status='LC'
		)
		self.location = Location.objects.create(name='Botanic Gardens')

	def _audio(self, name='test.wav'):
		return SimpleUploadedFile(name, b'audio-bytes', content_type='audio/wav')

	def _make_recording(self, name='rec.wav', flagged=False):
		return Recording.objects.create(
			user=self.user,
			species=self.species,
			location=self.location,
			audio_file=self._audio(name),
			date_recorded=timezone.now() - timedelta(hours=1),
			confidence_score=0.75,
			flagged=flagged,
		)

	# --- submit_recording ---

	def test_submit_recording_creates_recording(self):
		recording = submit_recording(
			user=self.user,
			species_id=self.species.pk,
			location_id=self.location.pk,
			audio_file=self._audio(),
			date_recorded=timezone.now() - timedelta(hours=1),
			confidence_score=0.88,
		)
		self.assertIsNotNone(recording.pk)
		self.assertEqual(recording.user, self.user)
		self.assertEqual(recording.species, self.species)
		self.assertEqual(recording.location, self.location)

	def test_submit_recording_raises_permission_denied_for_anonymous(self):
		with self.assertRaises(PermissionDenied):
			submit_recording(
				user=AnonymousUser(),
				species_id=self.species.pk,
				location_id=self.location.pk,
				audio_file=self._audio('anon.wav'),
				date_recorded=timezone.now(),
				confidence_score=0.5,
			)

	def test_submit_recording_raises_validation_error_for_invalid_species(self):
		with self.assertRaises(ValidationError):
			submit_recording(
				user=self.user,
				species_id=99999,
				location_id=self.location.pk,
				audio_file=self._audio('bad_species.wav'),
				date_recorded=timezone.now(),
				confidence_score=0.5,
			)

	def test_submit_recording_raises_validation_error_for_invalid_location(self):
		with self.assertRaises(ValidationError):
			submit_recording(
				user=self.user,
				species_id=self.species.pk,
				location_id=99999,
				audio_file=self._audio('bad_loc.wav'),
				date_recorded=timezone.now(),
				confidence_score=0.5,
			)

	# --- flag_recording ---

	def test_flag_recording_creates_anomaly_flag_and_marks_flagged(self):
		recording = self._make_recording('flag_happy.wav')
		flag = flag_recording(
			user=self.user,
			recording_id=recording.pk,
			anomaly_type='DISTORTION',
			description='Clipping at start',
		)
		self.assertIsNotNone(flag.pk)
		recording.refresh_from_db()
		self.assertTrue(recording.flagged)

	def test_flag_recording_raises_permission_denied_for_anonymous(self):
		recording = self._make_recording('flag_anon.wav')
		with self.assertRaises(PermissionDenied):
			flag_recording(
				user=AnonymousUser(),
				recording_id=recording.pk,
				anomaly_type='DISTORTION',
			)

	def test_flag_recording_raises_validation_error_for_missing_recording(self):
		with self.assertRaises(ValidationError):
			flag_recording(
				user=self.user,
				recording_id=99999,
				anomaly_type='DISTORTION',
			)

	def test_flag_recording_raises_validation_error_for_duplicate_flag(self):
		recording = self._make_recording('flag_dup.wav')
		flag_recording(user=self.user, recording_id=recording.pk, anomaly_type='DISTORTION')
		with self.assertRaises(ValidationError):
			flag_recording(user=self.user, recording_id=recording.pk, anomaly_type='DISTORTION')

	# --- review_recording ---

	def test_review_recording_clears_flags_and_marks_reviewed(self):
		recording = self._make_recording('review_happy.wav', flagged=True)
		AnomalyFlag.objects.create(
			recording=recording, flagged_by=self.user, anomaly_type='DISTORTION', description='Test'
		)
		result = review_recording(user=self.reviewer, recording_id=recording.pk)
		result.refresh_from_db()
		self.assertFalse(result.flagged)
		self.assertEqual(result.anomaly_flags.count(), 0)

	def test_review_recording_raises_permission_denied_for_non_reviewer(self):
		recording = self._make_recording('review_perm.wav', flagged=True)
		with self.assertRaises(PermissionDenied):
			review_recording(user=self.user, recording_id=recording.pk)

	def test_review_recording_raises_validation_error_for_missing_recording(self):
		with self.assertRaises(ValidationError):
			review_recording(user=self.reviewer, recording_id=99999)

	def test_review_recording_raises_validation_error_for_unflagged_recording(self):
		recording = self._make_recording('review_unflagged.wav', flagged=False)
		with self.assertRaises(ValidationError):
			review_recording(user=self.reviewer, recording_id=recording.pk)