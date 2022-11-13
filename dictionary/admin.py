from django.contrib import admin
from dictionary.models import WebContent, LatinWord


@admin.register(WebContent)
class WebContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'update_time', 'create_time')
    list_display_links = ('id', 'url')
    search_fields = ('id', 'url')
    ordering = ('-update_time', )


@admin.register(LatinWord)
class LatinWordAdmin(admin.ModelAdmin):
    list_display = ('id', 'words', 'word_class', 'main_attr', 'other_attrs', 'translated_meanings', 'status')
    list_display_links = ('id', 'words')
    search_fields = ('id', 'words')
    ordering = ('words', )
    list_filter = ('word_class', 'main_attr', 'other_attrs')

