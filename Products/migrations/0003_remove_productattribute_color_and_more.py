# Generated by Django 4.2.6 on 2023-10-27 01:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0002_alter_color_name_alter_size_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productattribute',
            name='color',
        ),
        migrations.RemoveField(
            model_name='productattribute',
            name='size',
        ),
    ]