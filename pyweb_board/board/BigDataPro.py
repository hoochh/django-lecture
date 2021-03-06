'''
Created on 2022. 7. 8.

@author: admin
'''


import requests
from bs4 import BeautifulSoup
from matplotlib import font_manager, rc
import matplotlib.pyplot as plt
import os
from pyweb_board.settings import STATIC_DIR, TEMPLATE_DIR #static = 이미지 등 template = 지도 등의 html 바로 저장 가능
from konlpy.tag._okt import Okt
from collections import Counter
import pytagcloud
import pandas as pd
import folium
from folium import plugins

def movie_crawling(data):
    for i in range(1,101):
        base='https://movie.naver.com/movie/point/af/list.naver?&page='
        url=base+str(i) # 1~100 페이지까지의 리뷰를 가져옴
        req=requests.get(url)
        if req.ok:
            html=req.text # text는 html 태그
            soup=BeautifulSoup(html,'html.parser')
            titles=soup.select('.title > a.movie')
            points=soup.select('.title em')
            contents=soup.select('.title')
            n=len(titles)
            
            for i in range(n):
                title=titles[i].get_text()
                point=points[i].get_text()
                contentArr=contents[i].get_text().replace('신고','').split('\n\n')
                content=contentArr[2].replace('\t','').replace('\n','')
                # list로 저장
                # data.append([title, point, content])
                
                # DB 저장시 튜플 형태로 저장
                data.append((title, point, content))
                print(title, point, content)
                
def makeGraph(titles,points):
    font_path="c:\Windows/fonts/malgun.ttf"
    font_name=font_manager.FontProperties(fname=font_path).get_name()
    rc('font',family=font_name)
    plt.title("영화 평점")
    plt.xlabel("영화 제목")
    plt.ylabel('평균평점')
    plt.grid(True)
    plt.bar(range(len(titles)),points, align='center')
    plt.xticks(range(len(titles)),list(titles),rotation=90)
    plt.savefig(os.path.join(STATIC_DIR,'images/fig01.png'),dpi=300)
    
def makeWordCloud(contents):
    nlp=Okt()
    fontname=''
    wordtext=""
    for t in contents:
        wordtext+=str(t)+" "
        
    nouns=nlp.nouns(wordtext)
    count=Counter(nouns) # 명사의 count를 셈
    wordInfo=dict()
    for tags, counts in count.most_common(100): 
        if(len(str(tags)) > 1): # 태그 길이가 1자보다 큰 것만 딕셔너리에 추가
            wordInfo[tags]=counts
            
    filename=os.path.join(STATIC_DIR,'images/wordcloud01.png')
    taglist=pytagcloud.make_tags(dict(wordInfo).items(),maxsize=80)
    pytagcloud.create_tag_image(taglist,filename, size=(800,600),
                                fontname='Korean', rectangular=False)
    
    # webbrowser(img)
    
def cctv_map():
    popup=[]
    data_lat_lng=[]
    a_path='C:/LYK/work/django/'
    df=pd.read_csv(os.path.join(a_path,'CCTV_20190917.csv'),encoding='CP949')
    print(pd)
    for data in df.values:
        if data[4] > 0: # data[4]는 cctv 개수. 개수가 1 이상일 때만 popup에 추가
            popup.append(data[1])
            data_lat_lng.append([data[10],data[11]]) # data[10], [11]은 위도 경도
            
    m=folium.Map([35.16242332,129.0441629],zoop_start=14)
    plugins.MarkerCluster(data_lat_lng,popups=popup).add_to(m)
    m.save(os.path.join(TEMPLATE_DIR,'map/map01.html'))
    
    
    