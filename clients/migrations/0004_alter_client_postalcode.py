# Generated by Django 5.1.7 on 2025-03-28 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0003_alter_client_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='postalcode',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
