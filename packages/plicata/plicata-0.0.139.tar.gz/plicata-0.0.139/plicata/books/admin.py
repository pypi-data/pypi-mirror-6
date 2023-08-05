from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from books.models import Book,Genre,Publisher, BookPage

class PublisherAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('publisher',)}

class GenreAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('genre',)}

class BookPageAdmin(Page):
    prepopulated_field = {'title': ('page.bookpage.thebook.title',)}

admin.site.register(Genre, GenreAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Book)
admin.site.register(BookPage, BookPageAdmin)
