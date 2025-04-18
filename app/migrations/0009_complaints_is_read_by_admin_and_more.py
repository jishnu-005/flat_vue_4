# Generated by Django 5.1.6 on 2025-04-02 07:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_notifications_complaints'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaints',
            name='is_read_by_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='complaints',
            name='is_read_by_user',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='complaints',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Resolved', 'Resolved'), ('Rejected', 'Rejected')], default='Pending', max_length=20),
        ),
        migrations.AddField(
            model_name='complaints',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='SupermarketCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.supermarketproduct')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.flatoccupant')),
            ],
        ),
        migrations.CreateModel(
            name='SupermarketOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Processing', 'Processing'), ('Dispatched', 'Dispatched'), ('Out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered'), ('Rejected', 'Rejected')], default='Pending', max_length=20)),
                ('payment_status', models.CharField(blank=True, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending', max_length=20, null=True)),
                ('placed_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('estimated_delivery', models.DateField(blank=True, null=True)),
                ('tracking_history', models.JSONField(default=dict)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.supermarketproduct')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='app.flatoccupant')),
            ],
        ),
        migrations.CreateModel(
            name='SupermarketPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending', max_length=20)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='app.supermarketorder')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.flatoccupant')),
            ],
        ),
    ]
