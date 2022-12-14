# Generated by Django 3.0.8 on 2020-08-30 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0006_latinword_sources'),
    ]

    operations = [
        migrations.AlterField(
            model_name='latinword',
            name='status',
            field=models.CharField(choices=[('DELETED', '删除'), ('NORMAL', '正常'), ('AUTO_TRANSLATED', '已机翻'), ('HIDDEN', '隐藏'), ('OCCURRED', '已出现'), ('TRANSLATED', '已翻译')], db_index=True, default='NORMAL', max_length=32, verbose_name='状态'),
        ),
        migrations.CreateModel(
            name='WordSearch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(db_index=True, max_length=255, verbose_name='单词')),
                ('info', models.IntegerField(db_index=True, verbose_name='详情ID')),
            ],
            options={
                'db_table': 'word_search',
                'unique_together': {('word', 'info')},
            },
        ),
    ]
