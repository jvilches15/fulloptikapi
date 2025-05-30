# Generated by Django 5.1.7 on 2025-05-02 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opticaweb', '0014_remove_consejo_imagen'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promocion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True)),
                ('fecha_inicio', models.DateField()),
                ('fecha_fin', models.DateField()),
                ('activa', models.BooleanField(default=True)),
            ],
        ),
    ]
