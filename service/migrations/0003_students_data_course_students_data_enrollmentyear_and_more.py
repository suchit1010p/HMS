# Generated by Django 5.1.7 on 2025-04-13 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0002_alter_students_data_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='students_data',
            name='course',
            field=models.CharField(default='BTech', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='students_data',
            name='enrollmentYear',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='students_data',
            name='programDuration',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='students_data',
            name='university',
            field=models.CharField(default='adani university', max_length=100),
            preserve_default=False,
        ),
    ]
