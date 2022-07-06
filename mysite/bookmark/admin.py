from django.contrib import admin
from bookmark.models import Bookmark

# Register your models here.
@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display=("id","title","url")
    
#admin.site.register(Bookmark, BookmarkAdmin) #@admin.register(Bookmark) 둘 중 하나 사용