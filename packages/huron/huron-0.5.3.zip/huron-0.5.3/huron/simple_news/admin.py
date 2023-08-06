from huron.simple_news.models import Category, News
from django.contrib import admin
from huron.utils.admin import CKEditorAdmin


class NewsAdmin(CKEditorAdmin):
    prepopulated_fields = {'slug': ('title',)}


class CategoryAdmin(CKEditorAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)
admin.site.register(News, NewsAdmin)
