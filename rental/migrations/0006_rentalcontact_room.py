# Generated by Django 4.2.13 on 2024-10-19 06:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0005_remove_rentalcontact_room'),
    ]

    operations = [
        migrations.AddField(
            model_name='rentalcontact',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rental_contacts', to='rental.room'),
        ),
    ]
