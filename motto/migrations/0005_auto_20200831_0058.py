# Generated by Django 3.0.8 on 2020-08-30 16:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0009_auto_20200830_1944'),
        ('motto', '0004_mottoword'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='mottoword',
            unique_together={('school', 'word_info')},
        ),
    ]
