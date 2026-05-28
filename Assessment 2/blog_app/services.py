from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
import os

from .authorization import RecordingAccessPolicy
from .models import AnomalyFlag, Recording, Species, Location


def submit_recording(*, user, species_id, location_id, audio_file, date_recorded, confidence_score):
    """
    Orchestrates creating a new Recording.

    Validates that the user has create permission, then writes the Recording
    row. Wrapped in transaction.atomic() so any unexpected DB failure rolls
    back cleanly.

    MOV files uploaded from Apple devices are ISOBMFF-compatible with MP4;
    the extension is changed to .mp4 before saving so browsers that support
    video/mp4 (Chrome, Edge, Firefox) can play the audio track without any
    re-encoding.

    Raises PermissionDenied if the user lacks create permission.
    Returns the newly created Recording instance.
    """
    if not RecordingAccessPolicy.can_create_recording(user):
        raise PermissionDenied("You do not have permission to submit recordings.")

    try:
        species = Species.objects.get(pk=species_id)
    except Species.DoesNotExist:
        raise ValidationError("Selected species does not exist.")

    try:
        location = Location.objects.get(pk=location_id)
    except Location.DoesNotExist:
        raise ValidationError("Selected location does not exist.")

    # MOV containers from Apple devices share the ISOBMFF format with MP4.
    # Serving as video/mp4 lets Chrome/Edge/Firefox decode the audio track.
    if audio_file.name.lower().endswith('.mov'):
        audio_file.name = os.path.splitext(audio_file.name)[0] + '.mp4'

    with transaction.atomic():
        recording = Recording.objects.create(
            user=user,
            species=species,
            location=location,
            audio_file=audio_file,
            date_recorded=date_recorded,
            confidence_score=confidence_score,
        )

    return recording


def flag_recording(*, user, recording_id, anomaly_type, description=""):
    """
    Orchestrates flagging a recording with an anomaly.

    Locks the Recording row with select_for_update so concurrent flag
    attempts on the same recording are serialised. Creates an AnomalyFlag
    and sets Recording.flagged = True, both within a single atomic
    transaction.

    Raises PermissionDenied if the user lacks review permission.
    Raises ValidationError if the recording does not exist or is already
    flagged with the same anomaly type by the same user.
    Returns the newly created AnomalyFlag instance.
    """
    if not RecordingAccessPolicy.can_flag_recording(user):
        raise PermissionDenied("You do not have permission to flag recordings.")

    with transaction.atomic():
        try:
            recording = Recording.objects.select_for_update().get(pk=recording_id)
        except Recording.DoesNotExist:
            raise ValidationError("Recording not found.")

        duplicate = AnomalyFlag.objects.filter(
            recording=recording,
            flagged_by=user,
            anomaly_type=anomaly_type,
        ).exists()
        if duplicate:
            raise ValidationError(
                "You have already flagged this recording with that anomaly type."
            )

        anomaly_flag = AnomalyFlag.objects.create(
            recording=recording,
            flagged_by=user,
            anomaly_type=anomaly_type,
            description=description,
        )

        if not recording.flagged:
            recording.flagged = True
            recording.save()

    return anomaly_flag


def review_recording(*, user, recording_id):
    """
    Orchestrates clearing the flagged status of a recording.

    Locks the Recording row with select_for_update, removes all associated
    AnomalyFlags, and sets Recording.flagged = False, atomically.

    Raises PermissionDenied if the user lacks review permission.
    Raises ValidationError if the recording does not exist or is not
    currently flagged.
    Returns the updated Recording instance.
    """
    if not RecordingAccessPolicy.can_review_recordings(user):
        raise PermissionDenied("You do not have permission to review recordings.")

    with transaction.atomic():
        try:
            recording = Recording.objects.select_for_update().get(pk=recording_id)
        except Recording.DoesNotExist:
            raise ValidationError("Recording not found.")

        if not recording.flagged:
            raise ValidationError("This recording is not currently flagged.")

        recording.anomaly_flags.all().delete()

        recording.flagged = False
        recording.save()

    return recording
