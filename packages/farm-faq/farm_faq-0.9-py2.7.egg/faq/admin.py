from django.contrib import admin

from .models import Category, Question
from .forms import QuestionAdminForm


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'title']
    list_display_links = ['title']


class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm
    list_display = ['order', 'question', 'active']
    list_display_links = ['question']


admin.site.register(Category, CategoryAdmin)
admin.site.register(Question, QuestionAdmin)
