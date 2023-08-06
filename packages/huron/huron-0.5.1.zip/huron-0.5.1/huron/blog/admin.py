from huron.blog.models import Post, Category
from django.contrib import admin
from huron.utils.admin import CKEditorAdmin


class PostAdmin(CKEditorAdmin):
    fields = ['pub_date', 'published','title', 'image', 'slug', 'short_desc', 'article', 'categories']
    prepopulated_fields = {'slug': ('title',)}

class CategoryAdmin(CKEditorAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
