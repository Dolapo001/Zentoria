# Generated by Django 4.2.6 on 2023-10-27 01:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Products', '0003_remove_productattribute_color_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProductAttribute',
        ),
    ]