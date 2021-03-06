from django.shortcuts import render
from bookmark.models import Bookmark
from django.views.generic.detail import DetailView
from django.views.generic import ListView, DeleteView

# Create your views here.
class BookmakrLV(ListView):
    model=Bookmark
    
class BookmarkDV(DetailView):
    model=Bookmark
    
def home(request):
    #select * from bookmark_bookmark order by title
    urlList=Bookmark.objects.order_by("title") #-title 내림차순 정렬
    #select count(*) from bookmark_bookmark
    urlCount =Bookmark.objects.all().count()
    #list.html 페이지로 넘어가서 출력됨 
    #rander("url",{"변수명“:값,"변수명“:값})
    return render(request,"bookmark/list.html", {"urlList":urlList, "urlCount":urlCount})

def detail(request):
    #get 방식 변수 받아오기 request.GET["변수명"] #post 방식 변수 받아오기 request.POST["변수명"]
    addr=request.GET["url"]
    #select * from bookmark_bookmark where url="..."
    dto=Bookmark.objects.get(url=addr)
    #detail.html로 포워딩
    return render(request, "bookmark/detail.html", {"dto":dto})