# Generated by Django 5.1.7 on 2025-05-09 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opticaweb', '0016_cita_rechazada'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cita',
            name='confirmada',
        ),
        migrations.RemoveField(
            model_name='cita',
            name='rechazada',
        ),
        migrations.AddField(
            model_name='cita',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('rechazada', 'Rechazada')], default='pendiente', max_length=10),
        ),
    ]
