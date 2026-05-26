from django.urls import path

from .views import (
    RecordingDetailView,
    RecordingListView,
    RecordingCreateView,
    FlagRecordingView,
    ReviewRecordingView,
    SpeciesAnalyticsView,
)

app_name = 'blog_app'

urlpatterns = [
    path('recordings/', RecordingListView.as_view(), name='recording-list'),
    path('recordings/new/', RecordingCreateView.as_view(), name='recording-create'),
    path('recordings/<int:pk>/', RecordingDetailView.as_view(), name='recording-detail'),
    path('recordings/<int:pk>/flag/', FlagRecordingView.as_view(), name='recording-flag'),
    path('recordings/<int:pk>/review/', ReviewRecordingView.as_view(), name='recording-review'),
    path('analytics/species/', SpeciesAnalyticsView.as_view(), name='species-analytics'),
]
