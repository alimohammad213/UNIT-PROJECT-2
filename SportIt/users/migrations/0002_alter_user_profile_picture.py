# Generated by Django 5.2 on 2025-04-12 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, default='images/default-profile.png', upload_to='images/'),
        ),
    ]
