# Generated by Django 4.1 on 2024-08-13 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='date_of_join',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='pov',
            field=models.TextField(null=True),
        ),
    ]
