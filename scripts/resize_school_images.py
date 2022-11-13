#-*- coding: utf-8 -*-
import os
from django.conf import settings
from PIL import Image
from motto.models import School
from tqdm import tqdm


def run():
    schools = []
    for school in School.objects.all():
        if str(school.logo) != '':
            schools.append(school)
        elif str(school.image1) != '':
            schools.append(school)
        elif str(school.image2) != '':
            schools.append(school)

    target_size = 128
    png_suffix = '.{}.png'.format(target_size)
    jpg_suffix = '.{}.jpg'.format(target_size)
    count = 0
    for school in tqdm(schools, ascii=True):
        logo_path = str(school.logo)
        if logo_path.endswith(png_suffix):
            origin_path = logo_path[:-len(png_suffix)]
            if os.path.exists(origin_path):
                logo_path = origin_path
            # img = Image.open(logo_path)
            # img = img.convert('RGB')
            # img.save(target_path)
            # school.logo = str(school.logo)[:-3] + 'jpg'
            # school.save()
        elif logo_path.endswith(jpg_suffix):
            origin_path = logo_path[:-len(jpg_suffix)]
            if os.path.exists(origin_path):
                logo_path = origin_path

        img = Image.open(os.path.join(settings.BASE_DIR, logo_path))
        img.thumbnail((target_size, target_size))
        img = img.convert('RGBA')
        try:
            target_path = os.path.join(settings.BASE_DIR, logo_path + png_suffix)
            img.save(target_path)
            school.logo = logo_path + png_suffix
            school.save()
        except Exception as ex:
            print('error', logo_path)
            raise ex

