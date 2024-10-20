# Generated by Django 4.2.13 on 2024-10-19 06:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0006_rentalcontact_room'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rentalcontact',
            name='bed',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rental_contact', to='rental.bed'),
        ),
    ]