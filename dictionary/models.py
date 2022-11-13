#-*- coding: utf-8 -*-
import json
import requests
from django.db import models
from django.db.utils import IntegrityError
from django.db.models import Q


class WebContent(models.Model):
    url = models.CharField("URL", max_length=255, unique=True)
    content = models.TextField("html内容", blank=True)
    update_time = models.DateTimeField("更新时间", auto_now=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        db_table = "web_content"


    @staticmethod
    def get_content(url, proxies=None):
        if len(url) <= 255:
            web_content = WebContent.objects.filter(url=url).first()
            if web_content is not None:
                return web_content.content
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}
        request_params = {'headers': headers, 'timeout': 30}
        if proxies is not None:
            request_params['proxies'] = proxies
        response = requests.get(url, **request_params)
        try:
            response.raise_for_status()
        except KeyboardInterrupt as ex:
            raise ex
        except Exception as ex:
            print(url, ex)
            return None
        if len(url) <= 255:
            try:
                WebContent.objects.create(url=url, content=response.text)
            except IntegrityError as ex:
                print(url, ex)
                return None
        return response.text


class LatinWord(models.Model):
    WORD_CLASSES = (
        ('noun', '名词'),
        ('verb', '动词'),
        ('adverb', '副词'),
        ('adjective', '形容词'),
        ('preposition', '介词'),
        ('conjunction', '连接词'),
        ('interjection', '感叹词'),
        ('numeral', '数词'),
        ('reflexive pronoun', '反身代词'),
        ('indefinite pronoun', '不定代词'),
        ('interrogative pronoun', '疑问代词'),
        ('adjectival pronoun', ''),
        ('demonstrative pronoun', '指示代词'),
        ('personal pronoun', '人称代词'),
        ('relative pronoun', '关系代词'),
        ('other pronoun', '其他代词'),
        ('', ''),
    )
    MAIN_ATTRS = (
        ("I Declension", "第一变格"),
        ("I and II Declension", "第一/第二变格"),
        ("II Declension", "第二变格"),
        ("III Declension", "第三变格"),
        ("IV Declension", "第四变格"),
        ("V Declension", "第五变格"),
        ("Indeclinable", ""),
        ("Irregular Declension", ""),
        ("Irregular", ""),
        ("I Conjugation", "第一变位"),
        ("II Conjugation", "第二变位"),
        ("III Conjugation", "第三变位"),
        ("IV Conjugation", "第四变位"),
        ("", ""),
    )
    
    OTHER_ATTRS = (
        ('Masculine', '阳性'),
        ('Feminine', '阴性'),
        ('Neuter', '中性'),
        ('Common', ''),
        ('All/Other', ''),
        ('Positive', ''),
        ('Distributive', ''),
        ('Ablative', ''),
        ('Accusative', ''),
        ('Adverbial', ''),
        ('Cardinal', ''),
        ('Ordinal', ''),
        ('Genitive', ''),
        ('Superlative', '最高级'),
        ('Comparative', '比较级'),
        ('', ''),
    )

    STATUS = (
        ("DELETED", "删除"),
        ("NORMAL", "正常"),
        ("AUTO_TRANSLATED", "已机翻"),
        ("HIDDEN", "隐藏"),
        ("OCCURRED", "已出现"),
        ("TRANSLATED", "已翻译"),
    )

    words = models.CharField("单词列表", max_length=255, db_index=True)
    word_class = models.CharField('词类', max_length=64, db_index=True, choices=WORD_CLASSES)
    main_attr = models.CharField('变位/变格', max_length=64, db_index=True, choices=MAIN_ATTRS, blank=True)
    other_attrs = models.CharField('其他属性', max_length=64, db_index=True, choices=OTHER_ATTRS, blank=True)
    raw_meanings = models.TextField('原始释义')
    translated_meanings = models.TextField('翻译释义')
    status = models.CharField("状态", max_length=32, db_index=True, choices=STATUS, default="NORMAL")
    sources = models.TextField("来源", default='[]')
    update_time = models.DateTimeField("更新时间", auto_now=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    
    class Meta:
        db_table = "latin_word"

    def __str__(self):
        return '{}:{}'.format(self.id, self.words)

    @staticmethod
    def search(raw_search_word, return_all=False):
        lower_search_word = raw_search_word.lower()
        search_words = [lower_search_word] + [lower_search_word[:i] for i in range(-1, -4, -1) if lower_search_word[:i] != '']
        filter_query = None
        for search_word in search_words:
            if filter_query is None:
                filter_query = Q(word__startswith=search_word)
            else:
                filter_query = filter_query | Q(word__startswith=search_word)

        info_ids = [i['info_id'] for i in WordSearch.objects.filter(filter_query).values('info_id').distinct()]

        word_info_list = []
        for word_info in LatinWord.objects.filter(id__in=list(info_ids)):
            score = 0
            for word in word_info.words.split(','):
                if word == raw_search_word:
                    score = max(score, 2000000)
                    break

                lower_word = word.lower()
                if lower_word == lower_search_word:
                    score = max(score, 1000000)

                if score >= 1000000:
                    continue
                for search_word in search_words:
                    if lower_word.startswith(search_word) and len(lower_word) - len(search_word) < 4:
                        score = max(score, len(search_word))
            word_info_list.append((score, word_info))

        if len(word_info_list) == 0:
            return []
        max_score = max([i[0] for i in word_info_list])
        word_info_list = [i for i in word_info_list if i[0] >= 1000000 or i[0] == max_score]
        search_results = [word_info[1] for word_info in sorted(word_info_list, key=lambda i: i[0], reverse=True)]

        if return_all:
            return search_results
        return search_results[:15]

    def json(self, compatible=True, lang='en'):
        print(self.id, self.words)
        data = {
            'id': self.id,
            'words': self.words.split(','),
            'word_class': self.word_class,
            'main_attr': self.main_attr,
            'other_attrs': self.other_attrs,
            'raw_meanings': json.loads(self.raw_meanings),
            'translated_meanings': json.loads(self.translated_meanings),
            'status': self.status,
            'sources': json.loads(self.sources),
            'update_time': self.update_time.strftime("%Y-%m-%d %H:%M:%S"),
            'create_time': self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if compatible:
            if lang == 'cn':
                data['class'] = self.get_word_class_display()
                data['attrs'] = [i for i in [self.get_main_attr_display(), self.get_other_attrs_display()] if i != '']
                data['meanings'] = data['translated_meanings']
            else:
                data['class'] = self.word_class
                data['attrs'] = [i for i in [self.main_attr, self.other_attrs] if i != '']
                data['meanings'] = data['raw_meanings']
        return data


class WordSearch(models.Model):
    word = models.CharField("单词", max_length=255, db_index=True)
    info_id = models.IntegerField("详情ID", db_index=True)

    class Meta:
        unique_together = ('word', 'info_id')
        db_table = "word_search"

