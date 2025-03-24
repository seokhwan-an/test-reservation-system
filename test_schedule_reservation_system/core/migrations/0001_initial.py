# Generated by Django 5.1.7 on 2025-03-24 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('role', models.CharField(choices=[('ADMIN', '관리자'), ('USER', '기업 고객')], max_length=20)),
            ],
        ),
    ]
