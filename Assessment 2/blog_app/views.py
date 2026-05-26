from django.db.models import Avg, Count, Q
from django.shortcuts import render, redirect
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Recording, Species
from .forms import RecordingForm
from .authorization import RecordingAccessPolicy


class RecordingQuerysetMixin:
	def get_base_queryset(self):
		return Recording.objects.with_related().with_quality_metrics()

	def get_authorized_queryset(self):
		return RecordingAccessPolicy.scope_recordings_queryset(self.request.user, self.get_base_queryset())


class RecordingListView(LoginRequiredMixin, RecordingQuerysetMixin, View):
	def get(self, request):
		queryset = self.get_authorized_queryset().order_by('-date_recorded')

		min_confidence = request.GET.get('min_confidence')
		if min_confidence:
			try:
				queryset = queryset.high_confidence(float(min_confidence))
			except ValueError:
				pass

		if request.GET.get('flagged_only') == 'true':
			if not RecordingAccessPolicy.can_review_recordings(request.user):
				raise PermissionDenied('You do not have permission to review flagged recordings.')
			queryset = queryset.flagged_or_anomalous()

		species_id = request.GET.get('species')
		if species_id:
			queryset = queryset.filter(species_id=species_id)

		context = {
			'recordings': queryset,
			'can_review_recordings': RecordingAccessPolicy.can_review_recordings(request.user),
		}

		return render(request, 'recording_list.html', context)


class RecordingDetailView(LoginRequiredMixin, RecordingQuerysetMixin, View):
	def get(self, request, pk):
		recording = self.get_authorized_queryset().filter(pk=pk).first()
		if not recording:
			raise Http404("Recording not found")

		context = {
			'recording': recording,
			'can_review_recordings': RecordingAccessPolicy.can_review_recordings(request.user),
		}

		return render(request, 'recording_detail.html', context)


class RecordingCreateView(LoginRequiredMixin, View):
	def _assert_create_permission(self, user):
		if not RecordingAccessPolicy.can_create_recording(user):
			raise PermissionDenied('You do not have permission to submit recordings.')

	def get(self, request):
		self._assert_create_permission(request.user)
		form = RecordingForm()
		context = {'form': form}
		return render(request, 'recording_form.html', context)

	def post(self, request):
		self._assert_create_permission(request.user)
		form = RecordingForm(request.POST, request.FILES)
		if form.is_valid():
			# Save the recording with the current user
			recording = form.save(commit=False)
			recording.user = request.user
			recording.save()
			
			# Redirect to the detail page
			return redirect('blog_app:recording-detail', pk=recording.pk)
		else:
			# Show form with errors
			context = {'form': form, 'errors': form.errors}
			return render(request, 'recording_form.html', context)


class SpeciesAnalyticsView(LoginRequiredMixin, View):
	def get(self, request):
		if not RecordingAccessPolicy.can_view_analytics(request.user):
			raise PermissionDenied('You do not have permission to view analytics.')

		species_rankings = (
			Species.objects.with_recording_stats()
			.filter(recording_count__gt=0)
			.order_by('-recording_count', 'name')
		)

		recording_totals = Recording.objects.aggregate(
			total_recordings=Count('id'),
			avg_confidence=Avg('confidence_score'),
			flagged_count=Count('id', filter=Q(flagged=True)),
		)

		context = {
			'summary': recording_totals,
			'species_rankings': species_rankings,
		}

		return render(request, 'analytics.html', context)
