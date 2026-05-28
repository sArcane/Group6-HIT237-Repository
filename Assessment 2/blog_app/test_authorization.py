from datetime import timedelta
from tempfile import TemporaryDirectory

from django.contrib.auth.models import Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Location, Recording, Species


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


class AuthorizationArchitectureTests(MediaIsolatedTestCase):
    def setUp(self):
        super().setUp()
        self.owner = User.objects.create_user(username='owner', password='pass12345')
        self.other_user = User.objects.create_user(username='other', password='pass12345')
        self.reviewer = User.objects.create_user(username='reviewer', password='pass12345')

        review_perm = Permission.objects.get(codename='review_recordings')
        analytics_perm = Permission.objects.get(codename='view_species_analytics')
        self.reviewer.user_permissions.add(review_perm, analytics_perm)

        self.species = Species.objects.create(name='Corella', scientific_name='Cacatua sanguinea', conservation_status='LC')
        self.location = Location.objects.create(name='Wetland')

        self.owner_recording = Recording.objects.create(
            user=self.owner,
            species=self.species,
            location=self.location,
            audio_file=SimpleUploadedFile('owner.wav', b'audio-1', content_type='audio/wav'),
            date_recorded=timezone.now() - timedelta(hours=3),
            confidence_score=0.9,
            flagged=False,
        )
        self.other_recording = Recording.objects.create(
            user=self.other_user,
            species=self.species,
            location=self.location,
            audio_file=SimpleUploadedFile('other.wav', b'audio-2', content_type='audio/wav'),
            date_recorded=timezone.now() - timedelta(hours=1),
            confidence_score=0.7,
            flagged=True,
        )

    def test_recording_list_requires_login(self):
        response = self.client.get(reverse('blog_app:recording-list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_owner_only_sees_own_recordings_without_global_permission(self):
        self.client.login(username='owner', password='pass12345')
        response = self.client.get(reverse('blog_app:recording-list'))
        self.assertEqual(response.status_code, 200)

        recordings = list(response.context['recordings'])
        self.assertEqual(len(recordings), 1)
        self.assertEqual(recordings[0].id, self.owner_recording.id)

    def test_reviewer_can_view_all_recordings(self):
        self.client.login(username='reviewer', password='pass12345')
        response = self.client.get(reverse('blog_app:recording-list'))
        self.assertEqual(response.status_code, 200)

        recordings = list(response.context['recordings'])
        ids = {recording.id for recording in recordings}
        self.assertIn(self.owner_recording.id, ids)
        self.assertIn(self.other_recording.id, ids)

    def test_analytics_denied_without_permission(self):
        self.client.login(username='owner', password='pass12345')
        response = self.client.get(reverse('blog_app:species-analytics'))
        self.assertEqual(response.status_code, 403)

    def test_analytics_allowed_with_permission(self):
        self.client.login(username='reviewer', password='pass12345')
        response = self.client.get(reverse('blog_app:species-analytics'))
        self.assertEqual(response.status_code, 200)
