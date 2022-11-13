from django.contrib import admin
from motto.models import Continent, Region, School, MottoWord, GrammarAbbreviation


@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = ('id', 'english_name', 'chinese_name', 'sort', 'status')
    list_display_links = ('id', )
    search_fields = ('id', 'english_name', 'chinese_name')
    list_filter = ('status', )
    list_editable = ('english_name', 'chinese_name', 'sort', 'status')
    ordering = ('-sort', )


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'continent', 'english_name', 'chinese_name', 'sort_name', 'extra')
    list_display_links = ('id', 'english_name', 'chinese_name')
    search_fields = ('id', 'english_name', 'chinese_name')
    list_editable = ('continent', )
    list_filter = ('extra', )
    ordering = ('english_name', )


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    # list_display = ('id', 'region', 'name', 'chinese_name', 'raw_motto', 'english_motto', 'chinese_motto', 'raw_motto_language', 'status')
    list_display = ('id', 'region', 'logo', 'name', 'english_name', 'chinese_name', 'raw_motto', 'status')
    search_fields = ('id', 'name', 'english_name', 'chinese_name')
    # list_editable = ('chinese_name', 'chinese_motto', 'status')
    list_editable = ('logo', 'status')
    list_display_links = ('name', )
    list_filter = ('status', 'translate_status', 'raw_motto_language', 'region')
    list_per_page = 9
    ordering = ('update_time', )


@admin.register(MottoWord)
class MottoWordAdmin(admin.ModelAdmin):
    list_display = ('id', 'school', 'school_motto', 'word', 'word_info_id', 'word_info_detail', 'status', 'sort')
    search_fields = ('id', 'word')
    list_editable = ('word', 'word_info_id', 'status')
    list_display_links = ('id', )
    ordering = ('school', 'sort')
    list_filter = ('status',)
    # list_filter = ('status')

@admin.register(GrammarAbbreviation)
class GrammarAbbreviationAdmin(admin.ModelAdmin):
    list_display = ('id', 'abbreviation', 'english_name', 'chinese_name', 'extra')
    search_fields = ('id', 'abbreviation', 'english_name', 'chinese_name')
    list_editable = ('abbreviation', 'english_name', 'chinese_name', 'extra')
    list_display_links = ('id', )
    ordering = ('abbreviation', )

