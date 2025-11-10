from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import User, Question, Answer, Tag

# Описание административного интерфейса.
@admin.register(User)
class UserAdmin(UserAdmin): # class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'is_active', 'created_at', 'updated_at')

    class AnswerInline(admin.TabularInline):
        model = Answer
        extra = 0

    inlines = (AnswerInline, )


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'author', 'is_active', 'created_at', 'updated_at')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title', )