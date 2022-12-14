# Generated by Django 3.0.8 on 2020-08-27 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0004_auto_20200826_2119'),
    ]

    operations = [
        migrations.AddField(
            model_name='latinword',
            name='status',
            field=models.CharField(choices=[('DELETED', '删除'), ('NORMAL', '正常'), ('HIDDEN', '隐藏'), ('OCCURRED', '已出现'), ('AUTO_TRANSLATED', '已机翻'), ('TRANSLATED', '已翻译')], db_index=True, default='NORMAL', max_length=32, verbose_name='状态'),
        ),
        migrations.AlterField(
            model_name='latinword',
            name='other_attrs',
            field=models.CharField(choices=[('Masculine', '阳性'), ('Feminine', '阴性'), ('Neuter', '中性'), ('Common', ''), ('All/Other', ''), ('Positive', ''), ('Distributive', ''), ('Ablative', ''), ('Accusative', ''), ('Adverbial', ''), ('Cardinal', ''), ('Ordinal', ''), ('Genitive', ''), ('Superlative', '最高级'), ('Comparative', '比较级'), ('', '')], db_index=True, max_length=64, verbose_name='其他属性'),
        ),
        migrations.AlterField(
            model_name='latinword',
            name='word_class',
            field=models.CharField(choices=[('noun', '名词'), ('verb', '动词'), ('adverb', '副词'), ('adjective', '形容词'), ('preposition', '介词'), ('conjunction', '连接词'), ('interjection', '感叹词'), ('numeral', '数词'), ('reflexive pronoun', '反身代词'), ('indefinite pronoun', '不定代词'), ('interrogative pronoun', '疑问代词'), ('adjectival pronoun', ''), ('demonstrative pronoun', '指示代词'), ('personal pronoun', '人称代词'), ('relative pronoun', '关系代词'), ('other pronoun', '其他代词'), ('', '')], db_index=True, max_length=64, verbose_name='词类'),
        ),
    ]
