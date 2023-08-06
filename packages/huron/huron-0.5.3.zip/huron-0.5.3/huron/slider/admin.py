from huron.slider.models import Slider, Slide
from huron.utils.admin import CKEditorAdmin

from django.contrib import admin


class SlideInline(admin.StackedInline):
    model = Slide
    extra = 3


class SliderAdmin(CKEditorAdmin):
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SlideInline]


class SlideAdmin(CKEditorAdmin):
    pass


admin.site.register(Slider, SliderAdmin)
