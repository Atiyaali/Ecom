# Generated by Django 5.0.6 on 2024-08-08 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_remove_order_details_tracking_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='price',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
