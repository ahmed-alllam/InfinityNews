# Generated by Django 3.0.3 on 2020-08-25 01:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('news', '0002_auto_20200819_1443'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('category', '-timestamp')},
        ),
    ]
