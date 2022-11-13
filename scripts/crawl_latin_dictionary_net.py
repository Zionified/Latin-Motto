#-*- coding: utf-8 -*-
import requests
import string
import json
import re
import copy
from tqdm import tqdm
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from django.db.utils import IntegrityError
from utils.translate import translate
from dictionary.models import WebContent


def crawl_directory():
    directory_entries = []
    for letter in tqdm(string.ascii_lowercase, desc="爬取目录中", ascii=True):
        html_content = WebContent.get_content("https://latin-dictionary.net/list/letter/" + letter)
        html = BeautifulSoup(html_content, 'html.parser')
        for li_tag in html.find('div', class_='list-items').find('ol').find_all('li', class_="word"):
            words = [i.strip() for i in li_tag.contents[0].text.split(',') if i.strip() != '-']
            words = [i.strip('(i)') for i in words]
            directory_entries.append({
                "word_detail_url": li_tag.contents[0]["href"],
                "words": json.dumps(words, ensure_ascii=False),
                "word_class": str(li_tag.contents[1]).strip(),
            })
    return directory_entries


def get_inline_text(tag):
    if isinstance(tag, NavigableString):
        return str(tag)
    if isinstance(tag, str):
        return tag
    return ''.join([get_inline_text(i) for i in tag.contents]).strip()


def crawl_words(directory_entries):
    directory_entries = copy.copy(directory_entries)

    # word_class_set = set()
    # grammar_map = {}
    word_class_map = {}

    no_gender_words = set()
    common_gender_words = set()

    word_set = set()
    repeated_words = set()
    for directory_entry in tqdm(directory_entries, desc="分析单词中", ascii=True):
        word_detail_url = directory_entry["word_detail_url"]
        html_content = WebContent.get_content(word_detail_url)
        html = BeautifulSoup(html_content, 'html.parser')
        entry_tag = html.find('div', id="corpus-content").find('div', class_="entry")
        try:
            words = [i.strip() for i in entry_tag.find('div', class_='banner banner-red').find('h3').find('a').text.split(',') if i.strip() != '-']
        except Exception as ex:
            raise ex
        entry_content_tag = entry_tag.find('div', class_="entry-content")

        # 词类
        word_class_tag = entry_content_tag.find('p', class_=re.compile('^speech speech-.*$'))
        # word_class_set.add(word_class_tag.text)
        word_class = word_class_tag.text
        if word_class_map.get(word_class) is None:
            word_class_map[word_class] = {}
        grammar_map = word_class_map[word_class]

        for word in words:
            if (word, word_class) in word_set:
                repeated_words.add((word, word_class))
            word_set.add((word, word_class))

        # 词性
        if entry_content_tag.find('div', class_="grammar").find('ul') is not None:
            for grammar_item_tag in entry_content_tag.find('div', class_="grammar").find('ul').find_all('li'):
                grammar_name = grammar_item_tag.find('span', class_='name').text
                grammar_value_tag = grammar_item_tag.find('span', class_='value')
                if grammar_name == 'conjugation':
                    grammar_value = get_inline_text(grammar_value_tag)
                else:
                    grammar_value = grammar_value_tag.text

                if grammar_name not in grammar_map:
                    grammar_map[grammar_name] = set()
                grammar_map[grammar_name].add(grammar_value)

                if grammar_name == 'gender' and grammar_value == 'no gender':
                    for word in words:
                        no_gender_words.add(word)
                if grammar_name == 'gender' and grammar_value == 'common':
                    for word in words:
                        common_gender_words.add(word)

        if 'conjugation' in grammar_map and 'declension' in grammar_map:
            print(words, ':', word_detail_url)

        # 定义
        definitions = []
        if entry_content_tag.find('div', class_='definitions').find('ol') is not None:
            for definition_tag in entry_content_tag.find('div', class_='definitions').find('ol').find_all('li'):
                definition = get_inline_text(definition_tag).strip()
                if definition != "":
                    definitions.append(definition)
    print(len(word_set))
    # print(len(repeated_words))
    # print(word_class_set)
    # print(grammar_map)
    print('no gender words:', no_gender_words)
    # print('common gender words:', common_gender_words)


def run():
    directory_entries = crawl_directory()
    crawl_words(directory_entries)

