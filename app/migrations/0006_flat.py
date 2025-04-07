# Generated by Django 5.1.6 on 2025-04-02 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_medicalstore_medicine'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flat_number', models.CharField(max_length=20, unique=True)),
                ('floor', models.IntegerField()),
                ('block', models.CharField(blank=True, max_length=10, null=True)),
                ('square_footage', models.PositiveIntegerField(blank=True, null=True)),
                ('bedrooms', models.PositiveIntegerField(default=1)),
                ('is_occupied', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['block', 'floor', 'flat_number'],
            },
        ),
    ]
