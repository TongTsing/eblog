# Generated by Django 4.2.17 on 2025-01-08 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_blog_access_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blog',
            old_name='access_time',
            new_name='access_times',
        ),
    ]