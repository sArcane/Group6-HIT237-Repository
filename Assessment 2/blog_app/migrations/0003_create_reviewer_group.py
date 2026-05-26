from django.db import migrations


REVIEWER_PERMISSION_CODENAMES = [
    'view_recording',
    'view_anomalyflag',
    'view_all_recordings',
    'review_recordings',
    'view_species_analytics',
    'view_all_anomaly_flags',
]


def create_reviewer_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    reviewer_group, _ = Group.objects.get_or_create(name='Reviewer')

    permissions = Permission.objects.filter(
        content_type__app_label='blog_app',
        codename__in=REVIEWER_PERMISSION_CODENAMES,
    )
    reviewer_group.permissions.set(permissions)


def remove_reviewer_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Reviewer').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('blog_app', '0002_authorization_permissions'),
    ]

    operations = [
        migrations.RunPython(create_reviewer_group, reverse_code=remove_reviewer_group),
    ]
