#-*- coding: utf-8 -*-
from pypinyin import lazy_pinyin
from motto.models import School, Region
from tqdm import tqdm


def run():
    schools = [i for i in School.objects.all()]
    for school in tqdm(schools, ascii=True):
        sort_name = school.english_name.replace(' ', '').lower()
        chinese_sort_name = ''.join(lazy_pinyin(school.chinese_name)).lower()
        school.sort_name = sort_name
        school.cn_sort_name = chinese_sort_name
        school.save()

    regions = [i for i in Region.objects.all()]
    for region in tqdm(regions, ascii=True):
        sort_name = region.english_name.replace(' ', '').lower()
        chinese_sort_name = ''.join(lazy_pinyin(region.chinese_name)).lower()
        region.sort_name = sort_name
        region.cn_sort_name = chinese_sort_name
        region.save()

