#-*- coding: utf-8 -*-
import time
import sys
import json

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.debug import ExceptionReporter


class EnhanceMiddleware(object):
    exception_html = None

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            request.ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
        else:
            request.ip = request.META['REMOTE_ADDR']

        time_begin = time.time()
        response = self.get_response(request)
        time_end = time.time()

        if isinstance(response, int):
            error_code = response
            error_message = ''
            if error_code == -4:
                error_message = '参数格式错误'
            elif error_code == -3:
                error_message = '系统异常'
            elif error_code == -2:
                error_message = '权限不足'
            elif error_code == -1:
                error_message = '请先登录'
            response = {'code': error_code, 'msg': error_message}
        if isinstance(response, tuple):
            if len(response) != 2 or not isinstance(response[0], int):
                response = {'code': -3, 'msg': '系统异常'}
            else:
                error_code = response[0]
                if error_code == 0:
                    response = {'code': response[0], 'data': response[1]}
                elif isinstance(response[1], str):
                    response = {'code': response[0], 'msg': response[1]}
                else:
                    response = {'code': -3, 'msg': '系统异常'}

        if isinstance(response, str):
            response = HttpResponse(response)
        elif type(response) in [dict, list]:
            response = JsonResponse(response)

        return response

    def process_exception(self, request, exception):
        exc_info = sys.exc_info()
        if exc_info != (None, None, None):
            self.exception_html = ExceptionReporter(request, *exc_info).get_traceback_html()

