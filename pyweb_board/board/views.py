from django.shortcuts import render, redirect
from board.models import Board,Comment,Movie
from django.views.decorators.csrf import csrf_exempt
# from django.utils.http import urlquote
from django.http.response import HttpResponse, HttpResponseRedirect
from django.db.models import Q

import os
import math
from board import BigDataPro
import pandas as pd
from django.db.models.aggregates import Avg

UPLOAD_DIR='C:/LYK/work/django/upload/'
# Create your views here.

def home(request):
    return render(request,'main.html')


def movie_save(request):
    data=[]
    BigDataPro.movie_crawling(data)
    # 하나씩 저장
    for row in data:
        dto=Movie(title=row[0],point=row[1],content=row[2])
        dto.save()
        
    return redirect('/')
    

def chart(request):
    data=Movie.objects.values('title').annotate(point_avg=Avg('point')).order_by('point_avg')[0:20]
    # title의 value 값으로 group_by 하여 point의 평균을 구함 -> annotate 하여 그 변수로 둔다
    # order_by로 역순 정렬 10개만 가져옴 
    df=pd.DataFrame(data)
    BigDataPro.makeGraph(df.title, df.point_avg)
    return render(request, 'bigdata_pro/chart.html',{'data':data})

def wordcloud(request):
    content=Movie.objects.values('content')
    df=pd.DataFrame(content)
    BigDataPro.makeWordCloud(df.content)
    return render(request,'bigdata_pro/wordcloud.html',{'content':df.content})

def cctv_map(request):
    BigDataPro.cctv_map()
    return render(request, 'map/map01.html')
    
    
# def list(request):
#     boardCount=Board.objects.count() 
#     boardList=Board.objects.all().order_by("-idx")
#     return render(request,"board/list.html", {"boardList":boardList, "boardCount":boardCount})
@csrf_exempt # form이 있는 경우는 필요
def list(request):
    try:
        search_option=request.POST['search_option']
    except:
        search_option=''
    
    try:
        search=request.POST['search']
    except:
        search=''
        
    if search_option=='all':
        boardCount=Board.objects.filter(Q(writer__contains=search)
                                        |Q(title__contains=search)
                                        |Q(content__contains=search)).count()
    elif search_option=='writer':
        boardCount=Board.objects.filter(Q(writer__contains=search)).count()
    elif search_option=='title':
        boardCount=Board.objects.filter(Q(title__contains=search)).count()
    elif search_option=='content':
        boardCount=Board.objects.filter(Q(content__contains=search)).count()
    else:
        boardCount=Board.objects.all().count()
       
    try:
        start=int(request.GET['start'])
    except:
        start=0
    
    page_size=5
    block_size=5
    
    end=start+page_size
    
    total_page=math.ceil(boardCount/page_size)
    current_page=math.ceil((start+1)/page_size)
    start_page=math.floor((current_page-1)/block_size)*block_size+1
    end_page=start_page+block_size-1
    
    if end_page > total_page:
        end_page=total_page
    
    print('total page:',total_page)
    print('current page:',current_page)
    print('start page:',start_page)
    print('end page:',start_page)
    
    if start_page >= block_size:
        prev_list=(start_page-2)*page_size
    else:
        prev_list=0
    
    if end_page < total_page:
        next_list=end_page*page_size
    else:
        next_list=0
     
    if search_option=='all':
        boardList=Board.objects.filter(Q(writer__contains=search)
                                        |Q(title__contains=search)
                                        |Q(content__contains=search)).order_by('-idx')[start:end]
    elif search_option=='writer':
        boardList=Board.objects.filter(Q(writer__contains=search)).order_by('-idx')[start:end]
    elif search_option=='title':
        boardList=Board.objects.filter(Q(title__contains=search)).order_by('-idx')[start:end]
    elif search_option=='content':
        boardList=Board.objects.filter(Q(content__contains=search)).order_by('-idx')[start:end]
    else:
        boardList=Board.objects.all().order_by('-idx')[start:end]
        
    links=[]
    for i in range(start_page, end_page+1):
        page_start=(i-1)*page_size
        links.append("<a href='/list/?start="+str(page_start)+"'>"+str(i)+"</a>")
        
    return render(request, 'board/list.html',
                  {'boardList': boardList,
                   'boardCount': boardCount,
                   "search_option": search_option,
                   "search": search,
                   "range":range(start_page-1,end_page),
                   "start_page":start_page,
                   "end_page":end_page,
                   "block_size":block_size,
                   "total_page":total_page,
                   "prev_list":prev_list, 
                   "next_list":next_list,
                   "links":links
                   })
    

def write(request):
    return render(request,"board/write.html")


@csrf_exempt
def insert(request):
    fname=''
    fsize=0
    
    if 'file' in request.FILES:
        file=request.FILES['file']
        fname=file.name
        fsize=file.size
        
        fp=open("%s%s" %(UPLOAD_DIR,fname),'wb')
        for chunk in file.chunks():
            # chunk : �뙆�씪�뿉�꽌 �븳 踰덉뿉 湲곕줉�븷 �닔 �엳�뒗 釉붾줉
            fp.write(chunk) # 湲곕줉�맖
        fp.close()
        
        w=request.POST['writer']
        t=request.POST['title']
        c=request.POST['content']
        
        dto=Board(writer=w, title=t, content=c, filename=fname, filesize=fsize)
        dto.save()
        return redirect('/list/')
    
    
def detail(request):
    id=request.GET['idx']
    dto=Board.objects.get(idx=id)
    dto.hit_up()
    dto.save()
    
    commentList=Comment.objects.filter(board_idx=id).order_by('-idx')
    filesize='%.2f'%(dto.filesize/1024)
    return render(request, 'board/detail.html',{'dto':dto, 'filesize':filesize, 'commentList':commentList})


def download(request): 
    id=request.GET['idx']
    dto=Board.objects.get(idx=id) 
    path=UPLOAD_DIR+dto.filename 
    filename=os.path.basename(path) 
    # filename=urlquote(filename) # 한글 인코딩을 위해 작성(에러 발생)
    with open(path,'rb') as file: 
        response=HttpResponse(file.read(), content_type='application/actet-stream')
        response['Content-Disposition']="attachment;filename*=UTF-8''{0}".format(filename)
        dto.down_up() 
        dto.save() 
        return response
    
    
@csrf_exempt
def reply_insert(request):
    id=request.POST['idx']
    dto=Comment(board_idx=id, writer=request.POST['writer'], content=request.POST['content'])
    dto.save()
    return HttpResponseRedirect('/detail?idx='+id)


@csrf_exempt 
def update(request):
    id=request.POST['idx']
    dto_src=Board.objects.get(idx=id)
    fname=dto_src.filename #기존 첨부파일 이름
    fsize=dto_src.filesize #기존 첨부파일 크기
    
    if "file" in request.FILES: #새로운 첨부파일이 있으면
        file=request.FILES['file']
        fname=file._name #새로운 첨부파일의 이름
        fp=open('%s%s' %(UPLOAD_DIR,fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()
        fsize=os.path.getsize(UPLOAD_DIR+fname)
        
    dto_new = Board(idx=id, writer=request.POST['writer'], title=request.POST['title'],
                    content=request.POST['content'],filename=fname, filesize=fsize)
    dto_new.save() #update query 호출 
    return redirect('/list/')


@csrf_exempt   
def delete(request):
    id=request.POST['idx']
    Board.objects.get(idx=id).delete()
    return redirect('/list/')    

    








    
    
    
    