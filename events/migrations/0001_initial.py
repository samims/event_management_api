# Generated by Django 3.0 on 2022-04-10 23:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('booking_code', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('-created_at',),
                'get_latest_by': 'created_at',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(db_index=True, max_length=255)),
                ('short_description', models.CharField(max_length=255)),
                ('long_description', models.TextField(blank=True, default='')),
                ('start_date', models.DateTimeField(db_index=True)),
                ('end_date', models.DateTimeField(db_index=True)),
                ('window_start_date', models.DateTimeField(db_index=True)),
                ('window_end_date', models.DateTimeField(db_index=True)),
                ('capacity', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to=settings.AUTH_USER_MODEL)),
                ('participants', models.ManyToManyField(related_name='participated_events', through='events.Booking', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-start_date'],
                'get_latest_by': 'start_date',
            },
        ),
        migrations.AddField(
            model_name='booking',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event'),
        ),
        migrations.AddField(
            model_name='booking',
            name='participant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]