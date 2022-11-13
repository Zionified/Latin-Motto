#-*- coding: utf-8 -*-
import requests
import string
import json
import re
import copy
import random
import threading
from functools import partial
from tqdm import tqdm
# from p_tqdm import p_uimap, p_map, p_imap
from django.db.models import Q
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from django.db.utils import IntegrityError
from utils.translate import translate
from dictionary.models import WebContent, LatinWord, WordSearch
from motto.models import School, MottoWord


def crawl_words():
    word_set = set()
    for web_content in WebContent.objects.filter(url__startswith="https://latin-dictionary.net/list/letter/"):
        html_content = web_content.content
        html = BeautifulSoup(html_content, 'html.parser')
        for li_tag in html.find('div', class_='list-items').find('ol').find_all('li', class_="word"):
            words = [i.strip() for i in li_tag.contents[0].text.split(',') if i.strip() != '-']
            for word in words:
                word_set.add(word)
    return word_set


PROXIES = None
def get_proxies():
    global PROXIES
    if PROXIES is None:
        api_proxy_response = requests.get('http://gea.ip3366.net/api/?key=20200722102653704&getnum=200&area=1&formats=2').json()
        PROXIES = ['http://{}:{}'.format(i['Ip'], i['Port']) for i in api_proxy_response]
    proxy_url = PROXIES[random.randint(0, len(PROXIES) - 1)]
    # return {'http': proxy_url, 'https': proxy_url}
    return None


def download_html_content(url):
    # return WebContent.get_content(url, proxies=get_proxies())
    return WebContent.get_content(url)


def crawl_search_pages(words):
    words = [i.replace('(i)', '').replace('(n)', '').replace('(ii)', '').strip('.').replace('/is', '') for i in words]
    words = list(set(words))
    with open('words.json', 'w') as f:
        f.write(json.dumps(words, indent=True))
    search_urls = ["http://www.latin-english.com/latin/{}/".format(word) for word in words]
    finished_urls = set([i['url'] for i in WebContent.objects.filter(url__startswith='http://www.latin-english.com/latin/').values('url')])
    search_urls = [url for url in list(set(search_urls)) if url not in finished_urls]


    def crawl_urls(i, urls):
        for search_url in tqdm(urls, desc="{}".format(i), ascii=True):
            try:
                download_html_content(search_url)
            except KeyboardInterrupt as ex:
                raise ex
            except Exception as ex:
                print(search_url, ex)
    
    num_cpus = 25
    min_item_count = len(search_urls) // num_cpus
    threads = []
    for i in range(num_cpus):
        if i == num_cpus - 1:
            urls = search_urls[i*min_item_count:]
        else:
            urls = search_urls[i*min_item_count:(i+1)*min_item_count]
        thread = threading.Thread(target=crawl_urls, args=(i, urls))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


def crawl_word_detail_pages():
    word_detail_urls = []
    for web_content in tqdm(WebContent.objects.filter(url__startswith='http://www.latin-english.com/latin/')):
        html = BeautifulSoup(web_content.content, 'html.parser')
        word_link_tags = html.find_all('a', href=re.compile(r'^/word/\d+/'))
        for word_link_tag in word_link_tags:
            word_detail_url = 'http://www.latin-english.com' + word_link_tag['href']
            word_detail_urls.append()
    word_detail_urls = list(set(word_detail_urls))
    for word_detail_url in tqdm(word_detail_urls):
        json_data = {'url': word_detail_url, 'headers': {}}
        requests.post('http://localhost:9000/api/task', json=json_data)

    
    with open('word_detail_urls.json', 'r') as f:
        word_detail_urls = json.loads(f.read())
    word_infos = []
    for word_detail_url in tqdm(word_detail_urls, ascii=True):
        # words = re.match(r'^http://www\.latin-english\.com/word/\d+/(.+)/$', word_detail_url).groups()[0]
        # words = list(filter(lambda s: s != '', map(lambda s: s.strip(), words.split('-'))))

        response = requests.get('http://localhost:9000/api/task', params={'url': word_detail_url}).json()
        task = response['data']['task']
        html = BeautifulSoup(task['response']['body'], 'html.parser')

        word_list_tag = html.find('a', href=re.compile('^/word/\d+/'))
        words = [i.strip() for i in ' '.join(str(word_list_tag.contents[0]).split(',')).split(' ') if i != '']

        content_tag = html.find('div', class_='content').find('div', class_='tab-pane active text-left')
        title_tag = content_tag.find('h3')
        
        word_class = str(title_tag.contents[0]).strip().lower()

        word_attrs = ' '.join(filter(lambda s: s != '', map(lambda s: s.strip(), title_tag.contents[1].text.strip().split(' '))))
        word_attrs = word_attrs.replace('(Greek)', '').strip()
        word_attrs = word_attrs.replace('(masculine and/or feminine)', '').strip()
        word_attrs = ' '.join([i.strip() for i in word_attrs.split(' ') if i.strip() != ''])

        try:
            meanings = []
            for meaning_li_tag in content_tag.find('ul', class_='word-meaning').find_all('li'):
                meaning = str(meaning_li_tag.find('p').text).strip()
                meanings.append(meaning)
        except Exception as ex:
            print(word_detail_url)
            raise ex

        word_infos.append({'words': words, 'url': word_detail_url, 'word_class': word_class, 'word_attrs': word_attrs, 'meanings': meanings})
    with open('word_infos.json', 'w') as f:
        f.write(json.dumps(word_infos, indent=True))


    with open('word_infos.json', 'r') as f:
        word_infos = json.loads(f.read())

    word_info_map = {}
    remain_attrs = set()
    for word_info in word_infos:
        # 获取词类
        word_class = word_info['word_class']
        if word_class == 'ddemonstrative pronoun':
            word_class = 'demonstrative pronoun'
        word_info['word_class'] = word_class

        # 获取单词属性
        word_attrs = word_info['word_attrs']
        word_attrs = word_attrs.replace('(Greek)', '').strip()
        word_attrs = word_attrs.replace('Greek', '').strip()
        word_attrs = word_attrs.replace('(masculine and/or feminine)', '').strip()
        word_attrs = word_attrs.replace('(w/ -u)', '').strip()
        word_attrs = word_attrs.replace('(w/ -ius)', '').strip()
        word_attrs = word_attrs.replace('w/', '').strip()
        word_attrs = re.sub(r'\(\d+\)', '', word_attrs).strip()
        word_attrs = ' '.join([i.strip() for i in word_attrs.split(' ') if i.strip() != ''])
        word_attrs = 'Irregular' if word_attrs == '' else word_attrs
        if word_class == 'noun' and word_attrs == 'II Declension':
            word_attrs = 'II Declension Neuter'
        word_info['word_attrs'] = word_attrs

        # 单词列表
        # 可能单词会包含(i)，或以/is结尾
        words = word_info['words']
        words = [word.strip() for word in words]
        words = [word for word in words if word not in ('(Genitive:', '-ius)', '-', '')]
        words = [word for word in words if not word.startswith('-') and not word.endswith('.')]
        words = [word for word in words if not word.startswith('(') or not word.endswith(')')]
        # words = [word[:-3] if word.endswith('/is') else word for word in words]
        # words = [word.replace('(i)', '') for word in words]
        if len(words) == 0:
            continue
        word_info['words'] = words

        # 合并含义
        info_tuple = (' '.join(words), word_class, word_attrs)
        if word_info_map.get(info_tuple) is None:
            word_info_map[info_tuple] = word_info
        else:
            word_info_map[info_tuple]['meanings'].extend(word_info['meanings'])
    word_infos = list(word_info_map.values())

    for word_info in tqdm(word_infos, ascii=True):
        words = word_info['words']
        word_class = word_info['word_class']
        word_attrs = word_info['word_attrs']
        meanings = word_info['meanings']

        main_attr, other_attrs = extract_word_attrs(word_attrs)

        word_list_str = ','.join(words)

        info_tuple = (word_list_str, word_class, main_attr, other_attrs)

        latin_word_info = LatinWord.objects.filter(
                words__exact=word_list_str, 
                word_class__exact=word_class, 
                main_attr__exact=main_attr, 
                other_attrs__exact=other_attrs).order_by('-id').first()
        if (latin_word_info is None or 
                latin_word_info.words != word_list_str or latin_word_info.word_class != word_class or 
                latin_word_info.main_attr != main_attr or latin_word_info.other_attrs != other_attrs):
            latin_word_info = LatinWord.objects.create(
                    words=word_list_str,
                    word_class=word_class,
                    main_attr=main_attr,
                    other_attrs=other_attrs,
                    raw_meanings=json.dumps(meanings),
                    translated_meanings='[]',
                    sources=json.dumps([word_info['url']]))
    for latin_word_info in tqdm(LatinWord.objects.values('id', 'words'), ascii=True):
        info_id = latin_word_info['id']
        words = latin_word_info['words'].split(',')
        words = [word[:-3] if word.endswith('/is') else word for word in words]
        words = [word.replace('(i)', '') for word in words]
        words = [word.lower() for word in words]
        for word in words:
            if WordSearch.objects.filter(word=word, info_id=info_id).first() is None:
                WordSearch.objects.create(word=word, info_id=info_id)


def extract_word_attrs(word_attrs):
    for prefix in [i[0] for i in LatinWord.MAIN_ATTRS]:
        if word_attrs.startswith(prefix):
            return prefix, word_attrs[len(prefix):].strip()


def translate_latin_words():
    for latin_word_id in tqdm([i['id'] for i in LatinWord.objects.filter(status='NORMAL').values('id')], ascii=True):
        try:
            latin_word_info = LatinWord.objects.filter(id=latin_word_id).first()
            raw_meanings = json.loads(latin_word_info.raw_meanings)
            translated_meanings = json.loads(latin_word_info.translated_meanings)
            if len(translated_meanings) > 0:
                continue
            for raw_meaning in raw_meanings:
                translated_meanings.append(translate(raw_meaning, dest="zh-cn").text)
            latin_word_info.translated_meanings = json.dumps(translated_meanings, ensure_ascii=False)
            latin_word_info.status = 'AUTO_TRANSLATED'
            latin_word_info.save()
        except Exception as ex:
            print(ex)


def mark_motto_words():
    # 校训分词
    for school in tqdm(School.objects.filter(raw_motto_language__contains='LATIN'), ascii=True):
        motto_words = school.get_motto_words()

        sort = 0
        for motto_word in motto_words:
            sort += 1
            motto_word_info = MottoWord.objects.filter(school=school, word=motto_word).first()
            if motto_word_info is None:
                motto_word_info = MottoWord.objects.create(school=school, word=motto_word, sort=sort)
            search_results = LatinWord.search(motto_word, return_all=True)
            if len(search_results) == 1:
                latin_word_info = search_results[0]
                if motto_word_info.word_info_id != latin_word_info.id:
                    motto_word_info.word_info_id = latin_word_info.id
                    motto_word_info.status = 'NORMAL'
                    motto_word_info.save()


def run():
    # words = crawl_words()
    # crawl_search_pages(words)
    # crawl_word_detail_pages()
    mark_motto_words()
    # translate_latin_words()

