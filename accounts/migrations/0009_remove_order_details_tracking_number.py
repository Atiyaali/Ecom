# Generated by Django 5.0.6 on 2024-08-08 07:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_order_order_details'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order_details',
            name='tracking_number',
        ),
    ]
