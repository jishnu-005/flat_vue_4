# Generated by Django 5.1.6 on 2025-04-05 10:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_chatroom_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=15)),
                ('visitor_type', models.CharField(choices=[('Expected', 'Expected'), ('Unexpected', 'Unexpected'), ('Delivery', 'Delivery'), ('Service', 'Service')], max_length=20)),
                ('purpose', models.TextField(blank=True, null=True)),
                ('vehicle_number', models.CharField(blank=True, max_length=20, null=True)),
                ('id_proof_type', models.CharField(blank=True, max_length=50, null=True)),
                ('id_proof_number', models.CharField(blank=True, max_length=50, null=True)),
                ('id_proof_image', models.ImageField(blank=True, null=True, upload_to='visitor_ids/')),
                ('expected_arrival', models.DateTimeField(blank=True, null=True)),
                ('actual_arrival', models.DateTimeField(blank=True, null=True)),
                ('actual_departure', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending Approval'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('CheckedIn', 'Checked In'), ('CheckedOut', 'Checked Out')], default='Pending', max_length=20)),
                ('is_unexpected', models.BooleanField(default=False)),
                ('verification_code', models.CharField(blank=True, max_length=8, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('checked_in_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checked_in_visitors', to='app.security')),
                ('checked_out_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='checked_out_visitors', to='app.security')),
                ('flat', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.flat')),
                ('requested_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.flatoccupant')),
            ],
        ),
    ]
