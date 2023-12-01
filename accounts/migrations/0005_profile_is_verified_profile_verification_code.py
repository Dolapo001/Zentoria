# Generated by Django 4.2.7 on 2023-11-22 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='verification_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]