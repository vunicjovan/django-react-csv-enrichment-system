# Generated by Django 3.2.6 on 2025-06-26 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transformer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedfile',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Completed', 'Completed'), ('Failed', 'Failed')], default='Pending', max_length=10),
        ),
    ]
