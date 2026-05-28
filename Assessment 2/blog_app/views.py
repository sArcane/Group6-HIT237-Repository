from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Avg, Count, Q
from django.http import Http404
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .authorization import RecordingAccessPolicy
from .forms import RecordingForm
from .models import Recording, Species
from .services import flag_recording, review_recording, submit_recording


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
	def get(self, request):
		if not RecordingAccessPolicy.can_create_recording(request.user):
			raise PermissionDenied('You do not have permission to submit recordings.')
		form = RecordingForm()
		return render(request, 'recording_form.html', {'form': form})

	def post(self, request):
		form = RecordingForm(request.POST, request.FILES)
		if form.is_valid():
			try:
				recording = submit_recording(
					user=request.user,
					species_id=form.cleaned_data['species'].pk,
					location_id=form.cleaned_data['location'].pk,
					audio_file=form.cleaned_data['audio_file'],
					date_recorded=form.cleaned_data['date_recorded'],
					confidence_score=form.cleaned_data['confidence_score'],
				)
				return redirect('blog_app:recording-detail', pk=recording.pk)
			except PermissionDenied as e:
				messages.error(request, str(e))
				return redirect('blog_app:recording-list')
			except ValidationError as e:
				messages.error(request, e.message)
				return redirect('blog_app:recording-list')
		context = {'form': form, 'errors': form.errors}
		return render(request, 'recording_form.html', context)


class FlagRecordingView(LoginRequiredMixin, View):
	"""POST-only view. Reviewer submits an anomaly flag on a recording."""
	def post(self, request, pk):
		anomaly_type = request.POST.get('anomaly_type', '')
		description = request.POST.get('description', '')
		try:
			flag_recording(
				user=request.user,
				recording_id=pk,
				anomaly_type=anomaly_type,
				description=description,
			)
			messages.success(request, 'Recording flagged successfully.')
		except PermissionDenied as e:
			messages.error(request, str(e))
		except ValidationError as e:
			messages.error(request, e.message)
		return redirect('blog_app:recording-detail', pk=pk)


class ReviewRecordingView(LoginRequiredMixin, View):
	"""POST-only view. Reviewer clears all flags and marks a recording as reviewed."""
	def post(self, request, pk):
		try:
			review_recording(
				user=request.user,
				recording_id=pk,
			)
			messages.success(request, 'Recording reviewed and flags cleared.')
		except PermissionDenied as e:
			messages.error(request, str(e))
		except ValidationError as e:
			messages.error(request, e.message)
		return redirect('blog_app:recording-detail', pk=pk)


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


class RegisterView(View):
	def get(self, request):
		if request.user.is_authenticated:
			return redirect('blog_app:recording-list')
		form = UserCreationForm()
		return render(request, 'registration/register.html', {'form': form})

	def post(self, request):
		if request.user.is_authenticated:
			return redirect('blog_app:recording-list')
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Account created! You can now sign in.')
			return redirect('login')
		return render(request, 'registration/register.html', {'form': form})


class RecordingDeleteView(LoginRequiredMixin, View):
	def post(self, request, pk):
		if not request.user.is_superuser:
			raise PermissionDenied('Only administrators can delete recordings.')
		try:
			recording = Recording.objects.get(pk=pk)
			recording.delete()
			messages.success(request, 'Recording deleted successfully.')
		except Recording.DoesNotExist:
			raise Http404('Recording not found.')
		return redirect('blog_app:recording-list')
