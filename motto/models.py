#-*- coding: utf-8 -*-
import re
from django.db import models
from django.conf import settings
from dictionary.models import LatinWord


class Continent(models.Model):
    STATUS = (
        ("DELETED", "删除"),
        ("NORMAL", "正常"),
        ("HIDDEN", "隐藏"),
    )
    chinese_name = models.CharField("中文名", max_length=128, unique=True)
    english_name = models.CharField("英语名", max_length=128, unique=True)
    sort = models.IntegerField('排序', default=0, db_index=True)
    status = models.CharField("状态", max_length=32, db_index=True, choices=STATUS, default="NORMAL")

    class Meta:
        db_table = "continent"

    def __str__(self):
        return '{}:{}:{}'.format(self.id, self.chinese_name, self.english_name)

    def json(self, lang='en'):
        data = {
            'id': self.id,
            'chinese_name': self.chinese_name,
            'english_name': self.english_name,
            'status': self.status,
        }
        if lang == 'cn':
            data['name'] = self.chinese_name
        else:
            data['name'] = self.english_name
        return data


class Region(models.Model):
    continent = models.ForeignKey('motto.Continent', on_delete=models.SET_NULL, null=True, default=None, blank=True)
    chinese_name = models.CharField("中文名", max_length=128, unique=True)
    english_name = models.CharField("英语名", max_length=128, unique=True)
    cn_sort_name = models.CharField("中文排序名", max_length=128, db_index=True, blank=True, default='')
    sort_name = models.CharField("排序名", max_length=128, db_index=True, blank=True)
    extra = models.CharField('额外信息', max_length=512, default='')

    class Meta:
        db_table = "region"

    def __str__(self):
        return self.chinese_name

    def json(self, lang='en'):
        return {
            'id': self.id,
            'name': self.chinese_name if lang == 'cn' else self.english_name,
            'chinese_name': self.chinese_name,
            'english_name': self.english_name,
            'sort_name': self.sort_name,
            'cn_sort_name': self.cn_sort_name,
        }



class School(models.Model):
    TRANSLATE_STATUS = (
        ("AUTO_TRANSLATE", "自动翻译"),
        ("CUSTOM_TRANSLATE", "自定义翻译"),
    )

    STATUS = (
        ("DELETED", "删除"),
        ("NORMAL", "正常"),
        ("HIDDEN", "隐藏"),
    )
    continent = models.ForeignKey('motto.Continent', on_delete=models.SET_NULL, null=True, default=None)
    region = models.ForeignKey("motto.Region", on_delete=models.CASCADE)
    logo = models.ImageField('logo', upload_to='uploads/logo/', blank=True, null=True, default=None)
    name = models.CharField("校名", max_length=128, unique=True)
    english_name = models.CharField("英语校名", max_length=128, unique=True, blank=True)
    chinese_name = models.CharField("中文校名", max_length=128, db_index=True, blank=True)
    sort_name = models.CharField("排序名", max_length=128, db_index=True, blank=True)
    cn_sort_name = models.CharField("中文排序名", max_length=128, db_index=True, blank=True, default='')

    raw_motto = models.CharField("原始内容", max_length=1024)
    raw_motto_language = models.CharField("内容语言类型", max_length=64, db_index=True)
    english_motto = models.CharField("英语翻译校训", max_length=1024, blank=True)
    chinese_motto = models.CharField("中文翻译校训", max_length=1024, blank=True)
    translate_status = models.CharField("翻译状态", max_length=32, choices=TRANSLATE_STATUS, default="AUTO_TRANSLATE")

    grammar = models.TextField("词法及句法", default="", blank=True)

    status = models.CharField("状态", max_length=32, db_index=True, choices=STATUS, default="NORMAL")
    update_time = models.DateTimeField("更新时间", auto_now=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    image1 = models.ImageField('image1', upload_to='uploads/image1/', blank=True, null=True, default=None)
    image2 = models.ImageField('image1', upload_to='uploads/image2/', blank=True, null=True, default=None)

    class Meta:
        db_table = "school"

    def __str__(self):
        return '{}:{}'.format(self.id, self.chinese_name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


    def json(self, with_detail=False, lang='en'):
        data = {
            'id': self.id,
            'name': self.name,
            'english_name': self.english_name,
            'chinese_name': self.chinese_name,
            'sort_name': self.sort_name,
            'cn_sort_name': self.cn_sort_name,
            'translate_status': self.translate_status,
            'status': self.status,
            'update_time': self.update_time.strftime("%Y-%m-%d %H:%M:%S"),
            'create_time': self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'raw_motto': self.raw_motto,
            'raw_motto_language': self.raw_motto_language,
            'english_motto': self.english_motto,
            'chinese_motto': self.chinese_motto,
        }
        if str(self.logo) != '':
            data['logo'] = 'https://{}{}'.format(settings.DOMAIN, self.logo.url)
        else:
            data['logo'] = ''
        if with_detail:
            data['region'] = self.region.json()
            data['grammar'] = self.grammar

            data['images'] = []
            if str(self.image1) != '':
                data['images'].append('https://{}{}'.format(settings.DOMAIN, self.image1.url))
            if str(self.image2) != '':
                data['images'].append('https://{}{}'.format(settings.DOMAIN, self.image2.url))

            # data['images'] = ['https://farseer810-static.oss-cn-shenzhen.aliyuncs.com/%E6%A0%A1%E5%9B%AD.jpg']
            data['words'] = []
            word_info_map = {}
            motto_words = [i for i in MottoWord.objects.filter(school=self, status='NORMAL').order_by('sort', 'id')]
            word_info_ids = [i.word_info_id for i in motto_words]
            if len(word_info_ids) > 0:
                for word_info in LatinWord.objects.filter(id__in=word_info_ids):
                    word_info_map[word_info.id] = word_info
                for motto_word_info in motto_words:
                    if word_info_map.get(motto_word_info.word_info_id) is None:
                        continue
                    word_info = word_info_map[motto_word_info.word_info_id]
                    data['words'].append(word_info.json(lang=lang))
                    data['words'][-1]['word'] = motto_word_info.word
                    data['words'][-1]['extra'] = motto_word_info.extra
        return data

    @staticmethod
    def split_by_symbol(items, symbol):
        result = []
        for item in items:
            result.extend(item.split(symbol))
        return result

    def get_motto_words(self):
        if self.name == 'Williams College':
            return ['liberalitate', 'armigeri']
        elif self.name == 'Johns Hopkins University':  # Johns Hopkins University
            return ['veritas', 'vos', 'liberabit']

        raw_motto = self.raw_motto
        symbols = [' ', ',', '!', '.', '\'', '/', '?', ';', '[', ']', ':', '-']
        motto_words = [raw_motto]
        for symbol in symbols:
            motto_words = [i.strip() for i in School.split_by_symbol(motto_words, symbol) if i.strip() != '' and re.search(r'\d+', i) is None]
        return motto_words


class MottoWord(models.Model):
    STATUS = (
        ("DELETED", "删除"),
        ("NORMAL", "正常"),
        ("HIDDEN", "隐藏"),
    )

    school = models.ForeignKey('motto.School', on_delete=models.CASCADE, db_index=True)
    word = models.CharField('单词', max_length=128, default='', db_index=True)
    # word_info = models.ForeignKey('dictionary.LatinWord', on_delete=models.CASCADE, blank=True, null=True)
    word_info_id = models.IntegerField('单词详情ID', default=0, db_index=True)
    sort = models.IntegerField('排序', default=0, db_index=True)
    status = models.CharField("状态", max_length=32, db_index=True, choices=STATUS, default="HIDDEN")
    extra = models.TextField('补充说明', default='')

    class Meta:
        # unique_together = ('school', 'word')
        db_table = "motto_word"

    @property
    def school_motto(self):
        school = self.school
        return '{}:{}'.format(school.raw_motto, school.chinese_motto)

    @property
    def word_info_detail(self):
        word_info_id = self.word_info_id
        if word_info_id is None or word_info_id == 0:
            return '--empty--'
        word_info = LatinWord.objects.filter(id=word_info_id).first()
        if word_info is None:
            return '--not found--'
        return '{}'.format(word_info.words)


class GrammarAbbreviation(models.Model):
    abbreviation = models.CharField("缩写", max_length=32, unique=True)
    english_name = models.CharField("英文名", max_length=64, blank=True)
    chinese_name = models.CharField("中文名", max_length=64, blank=True)
    extra = models.CharField('补充说明', max_length=512, default='', blank=True)

    class Meta:
        db_table = "grammar_abbreviation"

    def json(self, lang='en'):
        data = {
            'abbreviation': self.abbreviation,
            'english_name': self.english_name,
            'chinese_name': self.chinese_name,
            'extra': self.extra
        }
        data['content'] = []
        if lang == 'cn':
            data['name'] = self.chinese_name
            data['content'].append(self.chinese_name)
        else:
            data['name'] = self.english_name
            data['content'].append(self.english_name)
        if self.extra.strip() != "":
            data['content'].append(self.extra.strip())
        return data

