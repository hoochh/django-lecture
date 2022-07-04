from django.shortcuts import render
from bookmark.models import Bookmark
from django.views.generic.detail import DetailView
from django.views.generic import ListView, DeleteView

# Create your views here.
class BookmakrLV(ListView):
    model=Bookmark
    
class BookmarkDV(DetailView):
    model=Bookmark