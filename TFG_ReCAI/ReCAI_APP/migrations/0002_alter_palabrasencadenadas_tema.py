# Generated by Django 5.0.2 on 2024-02-25 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ReCAI_APP', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='palabrasencadenadas',
            name='tema',
            field=models.CharField(max_length=100),
        ),
    ]
