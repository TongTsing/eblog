# Generated by Django 4.2.17 on 2025-01-08 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_alter_blog_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='access_time',
            field=models.IntegerField(default=0),
        ),
    ]
