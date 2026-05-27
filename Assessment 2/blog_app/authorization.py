from django.contrib.auth.models import AnonymousUser


class RecordingAccessPolicy:
    VIEW_ALL_PERMISSION = 'blog_app.view_all_recordings'
    REVIEW_PERMISSION = 'blog_app.review_recordings'
    ANALYTICS_PERMISSION = 'blog_app.view_species_analytics'

    @classmethod
    def _is_authenticated(cls, user):
        return bool(user and not isinstance(user, AnonymousUser) and user.is_authenticated)

    @classmethod
    def can_view_all_recordings(cls, user):
        if not cls._is_authenticated(user):
            return False
        return user.is_superuser or user.has_perm(cls.VIEW_ALL_PERMISSION)

    @classmethod
    def can_review_recordings(cls, user):
        if not cls._is_authenticated(user):
            return False
        return user.is_superuser or user.has_perm(cls.REVIEW_PERMISSION)

    @classmethod
    def can_view_analytics(cls, user):
        return cls._is_authenticated(user)

    @classmethod
    def can_flag_recording(cls, user):
        return cls._is_authenticated(user)

    @classmethod
    def can_create_recording(cls, user):
        return cls._is_authenticated(user)

    @classmethod
    def scope_recordings_queryset(cls, user, queryset):
        if not cls._is_authenticated(user):
            return queryset.none()
        return queryset
