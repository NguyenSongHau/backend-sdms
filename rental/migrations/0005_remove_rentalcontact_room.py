# Generated by Django 4.2.13 on 2024-10-12 07:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0004_rentalcontact_room_alter_bed_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rentalcontact',
            name='room',
        ),
    ]
