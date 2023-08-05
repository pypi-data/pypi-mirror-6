from django.http import HttpResponseRedirect,HttpResponse
from mezzanine.pages.page_processors import processor_for
from .models import Book

@processor_for('books')
def WhatToNameThisFunction(request,page):
    booklist = Book.objects.filter(publisher_id=1).order_by('?') # order_by('?') randomizes the sort order
    return {'booklist':booklist} # add the 'booklist' to the dictionary then use it in the templates.

