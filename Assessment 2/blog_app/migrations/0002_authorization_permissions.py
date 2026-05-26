from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='anomalyflag',
            options={
                'permissions': [
                    ('view_all_anomaly_flags', 'Can view anomaly flags across all recordings'),
                ],
            },
        ),
        migrations.AlterModelOptions(
            name='recording',
            options={
                'permissions': [
                    ('view_all_recordings', 'Can view all recordings across users'),
                    ('review_recordings', 'Can review flagged recordings and anomalies'),
                ],
            },
        ),
        migrations.AlterModelOptions(
            name='species',
            options={
                'permissions': [
                    ('view_species_analytics', 'Can view species analytics dashboard'),
                ],
            },
        ),
    ]
