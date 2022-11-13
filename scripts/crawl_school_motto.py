#-*- coding: utf-8 -*-
import string
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from django.db.utils import IntegrityError
from motto.models import Region, School
from utils.translate import translate


def get_inner_text(tag):
    if isinstance(tag, NavigableString):
        return str(tag)
    if isinstance(tag, str):
        return tag
    return get_inner_text(tag.contents[0])


# 爬取校训数据
def crawl_mottos():
    """爬取校训数据
    @return: dict
    """

    """
    返回数据结构：{
        "region_name1": {
            "university_name1": {
                "language": "LANGUAGE",
                "raw_motto": "RAW_MOTTO",
                "english_motto": "ENGLISH_MOTTO"
            }
            "university_name2": {
                ...
            }
        },
        "region_name2": {
            ...
        }
    }
    """
    data = {}  # 返回数据
    response = requests.get('https://en.wikipedia.org/wiki/List_of_university_and_college_mottos')
    html = BeautifulSoup(response.text, 'html.parser')

    container_tag = html.find('div', class_="mw-parser-output")
    for index, child in enumerate(container_tag.contents):
        if child.name != "h2" and child.name != "table":
            continue
        if child.name == "h2":
            region_name_tag = child.find("span", class_="mw-headline")
            if region_name_tag == None:
                continue
            region_name = region_name_tag.text
            continue

        if not isinstance(child.get("class"), list) or len(child['class']) != 1 or child['class'][0] != "wikitable":
            continue

        if region_name not in data:
            data[region_name] = {}
        region_data = data[region_name]

        for tr_tag in child.find_all('tr')[1:]:
            td_tag_list = tr_tag.find_all('td')

            # 获取大学名
            if td_tag_list[0].find('a'):
                university_name = td_tag_list[0].find('a').text.strip()
            else:
                university_name = td_tag_list[0].text.strip()

            # 获取校训
            if region_name == "Philippines":
                raw_motto = get_inner_text(td_tag_list[2]).strip().strip('(').strip()
                # 获取语言
                if td_tag_list[3].find('a') is not None:
                    language = td_tag_list[3].find('a').text.strip()
                else:
                    language = td_tag_list[3].text.strip()
                language = language.upper()
            else:
                raw_motto = get_inner_text(td_tag_list[1]).strip().strip('(').strip()
                # 获取语言
                if td_tag_list[2].find('a') is not None:
                    language = td_tag_list[2].find('a').text.strip()
                else:
                    language = td_tag_list[2].text.strip()
                language = language.upper()

            # 获取英语翻译校训
            if language == "ENGLISH":
                english_motto = raw_motto
            elif len(td_tag_list) >= 4:
                if region_name == "Philippines":
                    english_motto = get_inner_text(td_tag_list[4]).strip().strip('(').strip()
                else:
                    english_motto = get_inner_text(td_tag_list[3]).strip().strip('(').strip()
            else:
                english_motto = ""

            if language == "":
                # 无官方校训
                raw_motto = ""
                english_motto = ""

            region_data[university_name] = {
                "language": language,
                "raw_motto": raw_motto,
                "english_motto": english_motto
            }

        ul_tag = None
        if index + 2 < len(container_tag.contents) and container_tag.contents[index+2].name == 'ul':
            ul_tag = container_tag.contents[index+2]
        if ul_tag and ul_tag.name == 'ul':
            for li_tag in ul_tag.find_all('li'):
                if len(li_tag.find_all('a')) != 2:
                    continue
                university_name, language = [tag.text.strip() for tag in li_tag.find_all('a')[:2]]
                language = language.upper()
                if li_tag.find('i') is None:
                    continue
                raw_motto = li_tag.find('i').text.strip()

                region_data[university_name] = {
                    "language": language,
                    "raw_motto": raw_motto,
                    "english_motto": ""
                }

    # 修正荷兰
    data["Netherlands"] = data["The Netherlands"]
    del data["The Netherlands"]
    return data


# 翻译地区名
def translate_region_name(region_name):
    # 有的自动翻译是错的，错误的国家地区翻译用以下映射表纠正
    correction_map = {
        "South Korea": "韩国",
        "Turkey": "土耳其",
        "Russia": "俄罗斯",
        "Georgia": "格鲁吉亚",
    }
    # 翻译地区名
    if region_name in correction_map:
        chinese_region_name = correction_map[region_name]
    else:
        chinese_region_name = translate(region_name, dest="zh-cn", src="en").text
    return chinese_region_name


# 翻译校名成英语
def get_english_school_name(school_name):
    correction_map = {
    }
    if school_name in correction_map:
        return correction_map[school_name]
    else:
        return translate(school_name, dest="en").text


# 翻译校名成英语
def get_chinese_school_name(school_name):
    correction_map = {
    }
    if school_name in correction_map:
        return correction_map[school_name]
    else:
        return translate(school_name, dest="zh-cn").text


def run():
    motto_data = crawl_mottos()

    # 添加地区
    region_model_map = {}
    for region in Region.objects.all():
        region_model_map[region.english_name] = region
    for region_name in motto_data:
        chinese_region_name = translate_region_name(region_name)
        sort_name = ''.join(region_name.lower().split(' '))

        # 插入或更新地区信息
        if region_name in region_model_map:
            region_model = region_model_map[region_name]
            region_model.chinese_name = chinese_region_name
            region_model.sort_name = sort_name
            region_model.save()
        else:
            region_model = Region.objects.create(english_name=region_name, chinese_name=chinese_region_name, sort_name=sort_name)
            region_model_map[region_name] = region_model


    # 添加学校与校训信息
    school_model_map = {}
    for school in School.objects.all():
        school_model_map[school.name] = school
    for region_name in tqdm(motto_data, desc="地区", ascii=True):
        region_model = region_model_map[region_name]
        for school_name in tqdm(motto_data[region_name], desc="学校", ascii=True):
            school_info = motto_data[region_name][school_name]
            raw_motto_language = school_info["language"]
            raw_motto = school_info["raw_motto"]
            english_motto = school_info["english_motto"]
            if english_motto == "" and raw_motto_language == "LATIN":
                english_motto = translate(raw_motto, dest="en", src="la").text

            chinese_motto = ""
            if raw_motto != "":
                if raw_motto_language in {"CHINESE", "TRADITIONAL CHINESE", "CLASSICAL CHINESE"}:
                    chinese_motto = raw_motto
                else:
                    chinese_motto = translate(english_motto, dest="zh-cn").text

            english_school_name = get_english_school_name(school_name)
            chinese_school_name = get_chinese_school_name(school_name)
            sort_name = ''.join(english_school_name.split(' '))

            # 插入或更新学校信息
            if school_name in school_model_map:
                school_model = school_model_map[school_name]
                if school_model.chinese_name == "":
                    school_model.chinese_name = chinese_school_name
                school_model.sort_name = sort_name
                if school_model.english_motto == "":
                    school_model.english_motto = english_motto
                if school_model.chinese_motto == "":
                    school_model.chinese_motto = chinese_motto
            else:
                school_model = School(
                    region=region_model,
                    name=school_name, 
                    english_name=english_school_name, 
                    chinese_name=chinese_school_name, 
                    sort_name=sort_name, 
                    raw_motto=raw_motto,
                    raw_motto_language=raw_motto_language,
                    english_motto=english_motto,
                    chinese_motto=chinese_motto,
                    translate_status="AUTO_TRANSLATE",
                    status="HIDDEN")
            try:
                school_model.save()
            except IntegrityError:
                school_model.english_name = school_model.english_name + "2"
                school_model.save()
            school_model_map[school_name] = school_model

    for school in School.objects.filter(raw_motto_language__contains='LATIN'):
        raw_motto = school.raw_motto
        symbols = [' ', ',', '!', '.', '\'', '/', '?', ';', '[', ']', ':', '-']
        replace_map = [('а', 'a'), ('і', 'i'), ('е', 'e'), ('о', 'o'), ('с', 'c'), ('—', '-'), ('Р', 'P'), ('æ', 'ae'), ('Æ', 'AE')]
        for replace_info in replace_map:
            raw_motto = raw_motto.replace(replace_info[0], replace_info[1])
        school.raw_motto = raw_motto
        school.save()

