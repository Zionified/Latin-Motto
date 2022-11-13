#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse
from dictionary.models import WebContent, LatinWord


def mock(request):
    url = request.GET.get('url', '')
    web_content = WebContent.objects.filter(url=url).first()
    if web_content is None:
        raise Http404('{}不存在'.format(url))
    return HttpResponse(web_content.content)


def search_words(request):
    try:
        search_words = request.GET['search_words'].strip()
        lang = request.GET.get('lang', 'en')
    except:
        return 0, []
    if search_words == '':
        return 0, []
    data = [i.json(lang=lang) for i in LatinWord.search(search_words)]
    return JsonResponse({'code': 0, 'data': data, 'search_words': search_words})


def get_word_detail(request):
    try:
        word_id = request.GET['id']
        lang = request.GET.get('lang', 'en')
    except:
        return 1, '单词不存在'
    latin_word_info = LatinWord.objects.filter(id=word_id).first()
    if latin_word_info is None:
        return 1, '单词不存在'
    return 0, latin_word_info.json(lang=lang)


def search_word_page(request):
    return render(request, 'search.html', {})

