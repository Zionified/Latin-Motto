"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from dictionary.views import mock
from dictionary import views as dictionary_views
from motto import views as motto_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('search', dictionary_views.search_word_page),
    path('api/word/search', dictionary_views.search_words),
    path('api/word/detail', dictionary_views.get_word_detail),
    path('api/school/search', motto_views.search_schools),
    path('api/school/detail', motto_views.get_school_detail),
    path('api/grammar_abbreviation/list', motto_views.get_grammar_abbreviations),
    path('api/continent/list', motto_views.get_continents),
    path('api/region/list', motto_views.get_regions),
    path('api/game_school/list', motto_views.get_game_schools),

    path('download/android', motto_views.download_android_page),
    path('download/ios', motto_views.download_ios_page),
    path('supports', motto_views.supports),
    path('privacy', motto_views.privacy),
    path('pioneer_research', motto_views.pioneer_research),
    path('package/<str:filename>', motto_views.download_android_package),
    path('mock/', mock),
]
