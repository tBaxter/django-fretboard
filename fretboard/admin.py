from django.contrib import admin
from fretboard.models import *


class CatAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')


class ForumAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'description', 'category', 'order')


class TopicAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'forum')
    search_fields = ['name']
    list_filter = ('forum',)


admin.site.register(Category, CatAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
