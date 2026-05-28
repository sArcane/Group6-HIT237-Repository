# Sequence Diagrams

Covers the five primary user flows: authentication, recording submission, recording list (with authorization scoping), anomaly flagging, and reviewer sign-off.

---

## 1. User Login

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant LoginView as Django LoginView<br/>(django.contrib.auth)
    participant DB as Database

    User->>Browser: GET /accounts/login/
    Browser->>LoginView: HTTP GET
    LoginView-->>Browser: Render login form

    User->>Browser: POST credentials
    Browser->>LoginView: HTTP POST (username, password)
    LoginView->>DB: authenticate(username, password)
    DB-->>LoginView: User | None

    alt Valid credentials
        LoginView->>DB: create session
        LoginView-->>Browser: 302 → /recordings/
    else Invalid credentials
        LoginView-->>Browser: 200 re-render form with error
    end
```

---

## 2. Submit Recording

```mermaid
sequenceDiagram
    actor User
    participant View as RecordingCreateView
    participant Policy as RecordingAccessPolicy
    participant Service as submit_recording()
    participant DB as Database

    User->>View: GET /recordings/new/
    View->>Policy: can_create_recording(user)
    Policy-->>View: True (authenticated)
    View-->>User: Render RecordingForm

    User->>View: POST form data + audio file
    View->>View: form.is_valid()

    alt Form invalid
        View-->>User: Re-render form with errors
    else Form valid
        View->>Service: submit_recording(user, species_id, location_id, audio_file, date_recorded, confidence_score)
        Service->>Policy: can_create_recording(user)

        alt Not authenticated
            Policy-->>Service: False
            Service-->>View: raise PermissionDenied
            View-->>User: messages.error → redirect /recordings/
        else Authenticated
            Policy-->>Service: True
            Service->>DB: Species.objects.get(pk=species_id)

            alt Species not found
                DB-->>Service: DoesNotExist
                Service-->>View: raise ValidationError
                View-->>User: messages.error → redirect /recordings/
            else Species found
                DB-->>Service: Species instance
                Service->>DB: Location.objects.get(pk=location_id)

                alt Location not found
                    DB-->>Service: DoesNotExist
                    Service-->>View: raise ValidationError
                    View-->>User: messages.error → redirect /recordings/
                else Location found
                    DB-->>Service: Location instance
                    Note over Service: .mov → .mp4 rename if needed
                    Service->>DB: Recording.objects.create(...) [atomic]
                    DB-->>Service: Recording instance
                    Service-->>View: Recording instance
                    View-->>User: 302 → /recordings/{id}/
                end
            end
        end
    end
```

---

## 3. View Recordings List (with Authorization Scoping)

```mermaid
sequenceDiagram
    actor User
    participant View as RecordingListView
    participant Mixin as RecordingQuerysetMixin
    participant Policy as RecordingAccessPolicy
    participant QS as RecordingQuerySet
    participant DB as Database

    User->>View: GET /recordings/
    View->>Mixin: get_authorized_queryset()
    Mixin->>QS: with_related().with_quality_metrics()
    Mixin->>Policy: scope_recordings_queryset(user, queryset)

    alt Superuser or has view_all_recordings / review_recordings
        Policy-->>Mixin: full queryset (all users)
    else Regular authenticated user
        Policy-->>Mixin: queryset.filter(user=request.user)
    end

    Mixin-->>View: scoped queryset

    Note over View: Apply optional filters:<br/>min_confidence, flagged_only, species

    View->>DB: execute queryset
    DB-->>View: Recording rows
    View-->>User: Render recording_list.html
```

---

## 4. Flag a Recording (Anomaly Report)

```mermaid
sequenceDiagram
    actor Reviewer
    participant View as FlagRecordingView
    participant Policy as RecordingAccessPolicy
    participant Service as flag_recording()
    participant DB as Database

    Reviewer->>View: POST /recordings/{pk}/flag/ (anomaly_type, description)
    View->>Service: flag_recording(user, recording_id, anomaly_type, description)
    Service->>Policy: can_flag_recording(user)

    alt Not authenticated
        Policy-->>Service: False
        Service-->>View: raise PermissionDenied
        View-->>Reviewer: messages.error → redirect detail page
    else Authenticated
        Policy-->>Service: True
        Service->>DB: Recording.objects.select_for_update().get(pk=recording_id) [atomic]

        alt Recording not found
            DB-->>Service: DoesNotExist
            Service-->>View: raise ValidationError("Recording not found.")
            View-->>Reviewer: messages.error → redirect detail page
        else Recording found
            DB-->>Service: Recording (locked)
            Service->>DB: AnomalyFlag.objects.filter(recording, flagged_by, anomaly_type).exists()

            alt Duplicate flag
                DB-->>Service: True
                Service-->>View: raise ValidationError("Already flagged with that type.")
                View-->>Reviewer: messages.error → redirect detail page
            else New flag
                DB-->>Service: False
                Service->>DB: AnomalyFlag.objects.create(...)
                Service->>DB: recording.flagged = True
                Service->>DB: recording.save()
                DB-->>Service: AnomalyFlag instance
                Service-->>View: AnomalyFlag instance
                View-->>Reviewer: messages.success → redirect detail page
            end
        end
    end
```

---

## 5. Review a Recording (Clear Flags)

```mermaid
sequenceDiagram
    actor Reviewer
    participant View as ReviewRecordingView
    participant Policy as RecordingAccessPolicy
    participant Service as review_recording()
    participant DB as Database

    Reviewer->>View: POST /recordings/{pk}/review/
    View->>Service: review_recording(user, recording_id)
    Service->>Policy: can_review_recordings(user)

    alt Not superuser / no review_recordings permission
        Policy-->>Service: False
        Service-->>View: raise PermissionDenied
        View-->>Reviewer: messages.error → redirect detail page
    else Authorised reviewer
        Policy-->>Service: True
        Service->>DB: Recording.objects.select_for_update().get(pk=recording_id) [atomic]

        alt Recording not found
            DB-->>Service: DoesNotExist
            Service-->>View: raise ValidationError("Recording not found.")
            View-->>Reviewer: messages.error → redirect detail page
        else Recording found
            DB-->>Service: Recording (locked)

            alt Not currently flagged
                Service-->>View: raise ValidationError("Not currently flagged.")
                View-->>Reviewer: messages.error → redirect detail page
            else Is flagged
                Service->>DB: recording.anomaly_flags.all().delete()
                Service->>DB: recording.flagged = False
                Service->>DB: recording.save()
                DB-->>Service: OK
                Service-->>View: Recording instance
                View-->>Reviewer: messages.success → redirect detail page
            end
        end
    end
```
