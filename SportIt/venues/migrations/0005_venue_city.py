# Generated by Django 5.2 on 2025-04-09 20:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0004_alter_venue_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='city',
            field=models.CharField(default='', max_length=100),
        ),
    ]
