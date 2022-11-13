#-*- coding: utf-8 -*-
from googletrans import Translator


translator = Translator(service_urls=["translate.google.cn"])
def detect(text):
    return Translator(service_urls=["translate.google.cn"]).detect(text)


def translate(text, dest='en', src='auto'):
    return Translator(service_urls=["translate.google.cn"]).translate(text, dest, src)

