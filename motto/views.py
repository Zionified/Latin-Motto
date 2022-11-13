#-*- coding: utf-8 -*-
import os
import json
import datetime
from django.conf import settings
from django.db.models import Q
from django.core.cache import cache
from django.shortcuts import render
from django.http import Http404, StreamingHttpResponse, FileResponse, JsonResponse
from motto.models import Continent, School, Region, GrammarAbbreviation
from dictionary.models import LatinWord


def search_schools(request):
    search_type = request.GET.get('type', 'name')
    search_type = 'name' if search_type != 'motto' else 'motto'
    search_words = request.GET.get('search_words', '')
    lang = request.GET.get('lang', 'en').lower()
    lang = 'en' if lang != 'cn' else 'cn'

    _filter = School.objects.filter(raw_motto_language='LATIN', status='NORMAL')

    start_time = datetime.datetime.now()
    continent_id = request.GET.get('continent', '')
    continent = None
    if continent_id != '':
        continent = Continent.objects.filter(id=continent_id, status='NORMAL').first()
        if continent is not None:
            _filter = _filter.filter(continent=continent)
    
    region_id = request.GET.get('region', '')
    region = None
    if region_id != '':
        region = Region.objects.filter(id=region_id).first()
        if region is not None:
            _filter = _filter.filter(region=region)

    if search_words == '':
        start_time = datetime.datetime.now()
        if continent is None and region is None:
            cache_key = 'cnlatin:schools:{}'.format(lang)
        elif continent is not None and region is None:
            cache_key = 'cnlatin:schools:{}:{}'.format(lang, continent.english_name.lower().replace(' ', ''))
        elif continent is None and region is not None:
            cache_key = 'cnlatin:schools:{}:{}'.format(lang, region.english_name.lower().replace(' ', ''))
        else:
            cache_key = 'cnlatin:schools:{}:{}:{}'.format(lang, continent.english_name.lower().replace(' ', ''), region.english_name.lower().replace(' ', ''))
        data = cache.get(cache_key)
        if data is None:
            if lang == 'cn':
                data = [school.json(lang=lang) for school in _filter.order_by('cn_sort_name')]
            else:
                data = [school.json(lang=lang) for school in _filter.order_by('sort_name')]
            cache.set(cache_key, json.dumps(data), timeout=60)
        else:
            data = json.loads(data)
    else:
        start_time = datetime.datetime.now()
        _filter = _filter.filter(Q(english_name__istartswith='university of ' + search_words) | Q(english_name__istartswith=search_words) | Q(chinese_name__istartswith=search_words) | Q(raw_motto__istartswith=search_words))
        if lang == 'cn':
            data = [school.json(lang=lang) for school in _filter.order_by('cn_sort_name')]
        else:
            data = [school.json(lang=lang) for school in _filter.order_by('sort_name')]
    return JsonResponse({'code': 0, 'data': data, 'search_words': search_words})


def get_school_detail(request):
    try:
        school_id = request.GET.get('id')
        lang = request.GET.get('lang', 'en')
    except:
        return 1, '学校不存在'
    if school_id is None:
        try:
            action = request.GET['action']
            current_school_id = int(request.GET['current_id'])
            if action not in ['next', 'last']:
                return -1, '参数错误'
        except:
            return -1, '参数错误'
        if action == 'next':
            school = School.objects.filter(id__gt=current_school_id, raw_motto_language='LATIN', status='NORMAL').order_by('id').first()
        else:
            school = School.objects.filter(id__lt=current_school_id, raw_motto_language='LATIN', status='NORMAL').order_by('-id').first()
        if school is None:
            return 2, '没有更多了'
    else:
        school = School.objects.filter(id=school_id).first()
    if school is None:
        return 1, '学校不存在'
    data = school.json(with_detail=True, lang=lang)

    # word_json = LatinWord.objects.first().json()
    # word_json['extra'] = '123'
    # data['words'] = [word_json]
    return 0, data


def get_grammar_abbreviations(request):
    lang = request.GET.get('lang', 'en')
    _filter = GrammarAbbreviation.objects.all().order_by('-abbreviation')
    data = [abbr.json(lang=lang) for abbr in _filter]
    return 0, data


def get_continents(request):
    lang = request.GET.get('lang', 'en')
    _filter = Continent.objects.filter(status='NORMAL').order_by('-sort')
    data = [i.json(lang=lang) for i in _filter]
    return 0, data


def get_regions(request):
    lang = request.GET.get('lang', 'en')
    if lang == 'cn':
        _filter = Region.objects.order_by('cn_sort_name')
    else:
        _filter = Region.objects.order_by('sort_name')
    data = [i.json(lang=lang) for i in _filter]
    return 0, data


def get_game_schools(request):
    lang = request.GET.get('lang', 'en')
    lang = 'en' if lang != 'cn' else 'cn'
    # 包含地区：美国、英国、加拿大、法国、德国、意大利、西班牙、日本、香港
    region_ids = [60, 8, 28, 59, 17, 18, 51, 27, 21]
    _filter = School.objects.filter(raw_motto_language='LATIN', status='NORMAL', region_id__in=region_ids)
    data = [school.json(lang=lang) for school in _filter]
    return 0, data


def humansize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def download_android_page(request):
    filename = '拉丁语学习.apk'
    package_path = os.path.join(settings.BASE_DIR, 'package', filename)
    try:
        filesize = os.path.getsize(package_path)
    except Exception as ex:
        filesize = 0
    data = {'version': '1.0.0', 'file_size': humansize(filesize), 'download_link': '/package/' + filename}
    return render(request, 'android.html', data)


def download_android_package(request, filename):
    package_path = os.path.join(settings.BASE_DIR, 'package', filename)
    if not os.path.exists(package_path):
        raise Http404('文件不存在')
    # response = StreamingHttpResponse(open(package_path, 'rb'))
    response = FileResponse(open(package_path, 'rb'))
    # response['Content-Type'] = 'application/vnd.android.package-archive'
    response['Content-Disposition'] = 'attachment;filename="{}"'.format('拉丁语学习.apk')
    return response


def download_ios_page(request):
    data = {'version': '1.0.0', 'download_link': '/package/ios'}
    return render(request, 'ios.html', data)


def supports(request):
    data = {}
    return render(request, 'supports.html', data)


def privacy(request):
    data = {}
    return render(request, 'privacy.html', data)


def pioneer_research(request):
    data = {}
    return render(request, 'pioneer_research.html', data)

