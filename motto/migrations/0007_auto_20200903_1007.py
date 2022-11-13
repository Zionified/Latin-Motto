# Generated by Django 3.0.8 on 2020-09-03 02:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0009_auto_20200830_1944'),
        ('motto', '0006_school_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='mottoword',
            name='word',
            field=models.CharField(db_index=True, default='', max_length=128, verbose_name='单词'),
        ),
        migrations.AlterField(
            model_name='mottoword',
            name='sort',
            field=models.IntegerField(db_index=True, default=0, verbose_name='排序'),
        ),
        migrations.AlterField(
            model_name='mottoword',
            name='word_info',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dictionary.LatinWord'),
        ),
        migrations.AlterField(
            model_name='school',
            name='logo',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='uploads/logo/', verbose_name='logo'),
        ),
        migrations.AlterUniqueTogether(
            name='mottoword',
            unique_together=set(),
        ),
    ]