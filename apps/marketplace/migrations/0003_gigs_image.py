# Generated by Django 5.2 on 2025-05-23 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0002_alter_gigs_table_alter_services_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='gigs',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='gig_images/'),
        ),
    ]
