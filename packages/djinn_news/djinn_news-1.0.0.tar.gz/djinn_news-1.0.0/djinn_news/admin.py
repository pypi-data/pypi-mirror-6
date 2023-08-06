from django.contrib import admin
from models.news import News


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', )
    search_fields = ['title']


admin.site.register(News, NewsAdmin)
