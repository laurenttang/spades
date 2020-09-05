#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Part1 引用套件

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, TemplateSendMessage, LocationSendMessage, StickerSendMessage
)
from linebot.models import (
    FlexSendMessage
)
from linebot.models.events import (
    PostbackEvent, FollowEvent
)
from linebot.models.template import(
    ButtonsTemplate, CarouselTemplate, CarouselColumn
)
from linebot.models import(
    PostbackAction, PostbackTemplateAction, MessageAction, MessageTemplateAction, URIAction, URITemplateAction
)
import os
import sys
import json
import time, random
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import pymysql
import logging
import pymysql.cursors

server_url="2f9e6d4125e2.ngrok.io"
# In[2]:


# 連接到MySQL資料庫
def connectDB():
    try:
        mysqldb = pymysql.connect(
                host="mysql",
                user="user",
                passwd="user",
                database="project",
                charset='utf8',
                port=3306,
                cursorclass=pymysql.cursors.DictCursor)
        return mysqldb
    except Exception as e:
        logging.error('Fail to connection mysql {}'.format(str(e)))
    return None


# In[3]:


#模擬推薦用的假資料
#fake_data = pd.read_csv('/home/spades/project/spades/env/fakedata.csv')
'''
print(fake_data)
print("==================================================")
print(fake_data.columns)
print("==================================================")
print(fake_data.columns[1])
print("==================================================")
print(fake_data['jobName'][0])
print("==================================================")
type(fake_data['jobName'][0])
'''

# In[4]:


# 爬取博客來求職/履歷面試類新書(取3筆)
def getnewbook():
    url='https://www.books.com.tw/web/sys_bbotm/books/020408/?v=1&o=1'
    res=requests.get(url)
    res.encoding='utf-8'
    headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
    soup=BeautifulSoup(res.text,'html.parser')
    m=soup.select('.mod_a')[0].select('.item')
    rank = 0
    title_list = []
    url_list = []
    for i in m:
        rank += 1
        title = i.find_all('h4')[0].text
        if len(title) > 20: title = title[0:20]
        title_list.append(title)
        url_list.append(i.select('a')[0]['href'])
        if rank == 3:
            return title_list, url_list #回傳標題跟連結網址

# 再用Flex Message顯示新書
def new_books():
    content = getnewbook()
    title_list = content[0] #標題
    url_list = content[1] #連結網址
    new_book_flex_message = FlexSendMessage(
            alt_text="博客來求職面試新書",
            contents=
            {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://imgur.com/gDtZ0YW.jpg",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "fit",
                    "action": {
                        "type": "uri",
                        "uri": "http://linecorp.com/"
                    },
                    "position": "relative",
                    "margin": "none"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "新書榜",
                        "weight": "bold",
                        "size": "xl",
                        "style": "normal"
                    }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                        "type": "uri",
                        "label": title_list[0],
                        "uri": url_list[0]
                        }
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                        "type": "uri",
                        "label": title_list[1],
                        "uri": url_list[1]
                        }
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": title_list[2],
                            "uri": url_list[2]
                        }
                    },
                    {
                        "type": "spacer",
                        "size": "sm"
                    }
                    ],
                    "flex": 0
                }
            }
    )
    return new_book_flex_message

# 爬取博客來求職/履歷面試類暢銷書(取3筆)
def getfamousbook():
    url='https://www.books.com.tw/web/sys_bbotm/books/020408/?v=1&o=5'
    res=requests.get(url)
    res.encoding='utf-8'
    headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
    soup=BeautifulSoup(res.text,'html.parser')
    m=soup.select('.mod_a')[0].select('.item')
    rank = 0
    title_list = []
    url_list = []
    for i in m:
        rank += 1
        title = i.find_all('h4')[0].text
        if len(title) > 20: title = title[0:20]
        title_list.append(title)
        url_list.append(i.select('a')[0]['href'])
        if rank == 3:
            return title_list, url_list #回傳標題跟連結網址

# 再用Flex Message顯示新書
def famous_books():
    content = getfamousbook()
    title_list = content[0] #標題
    url_list = content[1] #連結網址
    famous_book_flex_message = FlexSendMessage(
            alt_text="博客來求職面試暢銷書",
            contents={
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://imgur.com/knR6C5f.jpg",
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "fit",
                    "action": {
                    "type": "uri",
                    "uri": "http://linecorp.com/"
                    },
                    "position": "relative",
                    "margin": "none"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "暢銷榜",
                        "weight": "bold",
                        "size": "xl",
                        "style": "normal"
                    }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                        "type": "uri",
                        "label": title_list[0],
                        "uri": url_list[0]
                        }
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": title_list[1],
                            "uri": url_list[1]
                        }
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": title_list[2],
                            "uri": url_list[2]
                        }
                    },
                    {
                        "type": "spacer",
                        "size": "sm"
                    }
                    ],
                    "flex": 0
                }
        }
    )
    return famous_book_flex_message


# In[5]:


"""
天下雜誌-產業新聞
manufacturing 製造=6
service 服務=7
financial 金融=8
technology 科技=9
"""

# 爬取製造業新聞
def getManufacturingnews():
    url='https://www.cw.com.tw/subchannel.action?idSubChannel=6'
    res=requests.get(url)
    res.encoding='utf-8'
    headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
    soup=BeautifulSoup(res.text,'html.parser')
    m=soup.select('.main')[0].select('.article')
    rank = 0
    title_list = []
    url_list = []
    img_list=[]
    for i in m:
        rank += 1
        title = i.find_all('img')[0]['alt']
        title_list.append(title)
        url_list.append(i.select('a')[0]['href'])
        img_list.append(i.select('img')[0]['src'])
        if rank == 5:
            return title_list, url_list, img_list
        
def get_Manufacturing_news():
    content = getManufacturingnews()
    title_list = content[0] #文章標題
    url_list = content[1] #連結網址
    img_list = content[2] #新聞圖片
    
    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url= content[2][0],
                    title = content[0][0],
                    text = "製造業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][0]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][1],
                    title = content[0][1],
                    text = "製造業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][1]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][2],
                    title = content[0][2],
                    text = "製造業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][2]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][3],
                    title = content[0][3],
                    text = "製造業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][3]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][4],
                    title = content[0][4],
                    text = "製造業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][4]
                        ),
                    ]
                )  
            ]
        )
    )
    return carousel_template_message

# 爬取服務業新聞
def getServicenews():
    url='https://www.cw.com.tw/subchannel.action?idSubChannel=7'
    res=requests.get(url)
    res.encoding='utf-8'
    headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
    soup=BeautifulSoup(res.text,'html.parser')
    m=soup.select('.main')[0].select('.article')
    rank = 0
    title_list = []
    url_list = []
    img_list=[]
    for i in m:
        rank += 1
        title = i.find_all('img')[0]['alt']
        title_list.append(title)
        url_list.append(i.select('a')[0]['href'])
        img_list.append(i.select('img')[0]['src'])
        if rank == 5:
            return title_list, url_list, img_list
        
def get_Service_news():
    content = getServicenews()
    title_list = content[0] #文章標題
    url_list = content[1] #連結網址
    img_list = content[2] #新聞圖片
    
    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url= content[2][0],
                    title = content[0][0],
                    text = "服務業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][0]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][1],
                    title = content[0][1],
                    text = "服務業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][1]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][2],
                    title = content[0][2],
                    text = "服務業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][2]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][3],
                    title = content[0][3],
                    text = "服務業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][3]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][4],
                    title = content[0][4],
                    text = "服務業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][4]
                        ),
                    ]
                )  
            ]
        )
    )
    return carousel_template_message

# 爬取金融業新聞
def getFinancialnews():
    url='https://www.cw.com.tw/subchannel.action?idSubChannel=8'
    res=requests.get(url)
    res.encoding='utf-8'
    headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
    soup=BeautifulSoup(res.text,'html.parser')
    m=soup.select('.main')[0].select('.article')
    rank = 0
    title_list = []
    url_list = []
    img_list=[]
    for i in m:
        rank += 1
        title = i.find_all('img')[0]['alt']
        title_list.append(title)
        url_list.append(i.select('a')[0]['href'])
        img_list.append(i.select('img')[0]['src'])
        if rank == 5:
            return title_list, url_list, img_list
        
def get_Financial_news():
    content = getFinancialnews()
    title_list = content[0] #文章標題
    url_list = content[1] #連結網址
    img_list = content[2] #新聞圖片
    
    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url= content[2][0],
                    title = content[0][0],
                    text = "金融業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][0]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][1],
                    title = content[0][1],
                    text = "金融業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][1]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][2],
                    title = content[0][2],
                    text = "金融業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][2]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][3],
                    title = content[0][3],
                    text = "金融業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][3]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][4],
                    title = content[0][4],
                    text = "金融業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][4]
                        ),
                    ]
                )  
            ]
        )
    )
    return carousel_template_message

# 爬取科技業新聞
def getTechnologynews():
    url='https://www.cw.com.tw/subchannel.action?idSubChannel=9'
    res=requests.get(url)
    res.encoding='utf-8'
    headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
    soup=BeautifulSoup(res.text,'html.parser')
    m=soup.select('.main')[0].select('.article')
    rank = 0
    title_list = []
    url_list = []
    img_list=[]
    for i in m:
        rank += 1
        title = i.find_all('img')[0]['alt']
        title_list.append(title)
        url_list.append(i.select('a')[0]['href'])
        img_list.append(i.select('img')[0]['src'])
        if rank == 5:
            return title_list, url_list, img_list
        
def get_Technology_news():
    content = getTechnologynews()
    title_list = content[0] #文章標題
    url_list = content[1] #連結網址
    img_list = content[2] #新聞圖片
    
    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url= content[2][0],
                    title = content[0][0],
                    text = "科技業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][0]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][1],
                    title = content[0][1],
                    text = "科技業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][1]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][2],
                    title = content[0][2],
                    text = "科技業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][2]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][3],
                    title = content[0][3],
                    text = "科技業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][3]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url= content[2][4],
                    title = content[0][4],
                    text = "科技業",
                    actions=[
                        URIAction(
                            label="全文瀏覽",
                            uri=content[1][4]
                        ),
                    ]
                )  
            ]
        )
    )
    return carousel_template_message


# In[21]:


# 推薦 ++++++++++++++++++++++++++++++++++++++++
def recommend():
    db = connectDB()
  
    sql_2 = "select Code,if(LENGTH (jobName)>15,left(jobName,15),jobName) as jobName,if(LENGTH (companyName)>15,left(companyName,15),companyName) as companyName,salary,latitude,longitude from recom_2 order by id desc limit 3"
    
    fake_data = pd.read_sql(sql_2, db)
    print('與網頁版終極推薦一致:',fake_data)

    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://imgur.com/8pBiwX5.jpg',
                    title = fake_data['jobName'][0] + " " + fake_data['companyName'][0],
                    text = fake_data['salary'][0],
                    actions=[
                        URIAction(
                            label="地圖導覽",
                            uri="http://maps.google.com/maps?q={}{}{}".format(fake_data['latitude'][0], "," ,fake_data['longitude'][0]) 
                            # Google Map 範例：http://maps.google.com/maps?q=24.197611,120.780512
                            # 利用變更經緯度秀出各公司在Google Map地圖上的位置
                        ),
                        URIAction(
                            label='詳細資訊',
                            uri="https://www.104.com.tw/jobs/apply/analysis/" + fake_data["Code"][0]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url = 'https://imgur.com/K9cyKVj.jpg',
                    title = fake_data['jobName'][1] + " " + fake_data['companyName'][1],
                    text = fake_data['salary'][1],
                    actions=[
                        URIAction(
                            label="地圖導覽",
                            uri="http://maps.google.com/maps?q={}{}{}".format(fake_data['latitude'][1], "," ,fake_data['longitude'][1]) 
                        ),
                        URIAction(
                            label='詳細資訊',
                            uri="https://www.104.com.tw/jobs/apply/analysis/" + fake_data["Code"][1]
                        ),
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url = 'https://imgur.com/yFjNbB8.jpg',
                    title = fake_data['jobName'][2] + " " + fake_data['companyName'][2],
                    text = fake_data['salary'][2],
                    actions=[
                        URIAction(
                            label="地圖導覽",
                            uri="http://maps.google.com/maps?q={}{}{}".format(fake_data['latitude'][2], "," ,fake_data['longitude'][2]) 
                        ),
                        URIAction(
                            label='詳細資訊',
                            uri="https://www.104.com.tw/jobs/apply/analysis/" + fake_data["Code"][2]
                        ),
                    ]
                )
            ]
        )
    ),
    return carousel_template_message


# In[23]:===============================================================================================================================


# Part2 LineBotApi & WebhookHandler
app = Flask(__name__)


#line_bot_api = LineBotApi('TxD3RkH1Ff21Vq0nt3QFY7SLqJobvsqxLiJj3I7A+7bIo1QRwOBlcA2JrhDAEHaYgEl+U6s6mMMwxoxcVo4SxkLiq8F3hLWaOW5jdMPbK4ZdrvtllUZg7yDCY9BQnNk15iKiKHB0UX41PR/GSUZY9QdB04t89/1O/w1cDnyilFU=')
#handler = WebhookHandler('8993991f6415eb6229352822f94d98d9')


line_bot_api = LineBotApi('ib+QIt0ycYNeaghOsyOP89YrhX/c83m5rcy6mmgZDhdbhqMHAN4gyJwul1UISHQaFvGba0RMpOkFCW1aFUCorIXFVrax0DIkx7cIuI2WIbSFz2pFRm6g+5WyoSKLp9rSzRLcapIqB+adJ2exoqH0RQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('211a2220f5522291364aaac1f4099db0')

# ChatBot主體結構通常不會改變
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# 告知Handler，如果收到FollowEvent，則做下面的方法處理
# 追蹤事件
@handler.add(FollowEvent)
def handle_follow(event):
    print("in Follow")
    
    # 取出消息內User的資料
    user_profile = line_bot_api.get_profile(event.source.user_id)
    
    # print(user_profile.display_name)
    # print(user_profile.user_id)
    # print(user_profile.picture_url)
    # print(user_profile.status_message)
    
    # 將用戶資訊存在檔案內
    #with open("./users.txt", "a") as myfile:
    #    myfile.write(json.dumps(vars(user_profile),sort_keys=True))
    #    myfile.write('\r\n')
    
    
    
    # 官方範例：line_bot_api.push_message(to, TextSendMessage(text='Hello World!'))
    # Push Message裡要加userID
    # to的位置 => 放入userID
    user_id = user_profile.user_id
    line_bot_api.push_message(
        user_id,
        TextSendMessage(
            text="您好，歡迎使用「好缺勿濫」" # 推播公告
        )
    )
    
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage( #加入追蹤後的貼圖
            package_id='11537',
            sticker_id='52002735'
        )
    )

# 文字訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    
    # 當接收到「求職指南」後秀出Button Template
    if event.message.text == "求職指南":
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='求職指南',
                template=ButtonsTemplate(
                    title='求職類相關書籍',
                    text='請選擇您想觀看的部分',
                    actions=[
                        {
                            "type": "postback",
                            "label": "求職新書",
                            "text": "求職新書",
                            "data": "Book&new"
                        },
                        {
                            "type": "postback",
                            "label": "求職暢銷書",
                            "text": "求職暢銷書",
                            "data": "Book&famous"
                        },
                    ]
                )
            )
        )
    
    # 當接收到「產業新聞﹞後秀出Button Template
    if event.message.text == "產業新聞":
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text='產業新聞',
                template=ButtonsTemplate(
                    title='產業新聞',
                    text='請選擇您想觀看的新聞分類',
                    actions=[
                        {
                            "type": "postback",
                            "label": "製造業新聞",
                            "text": "製造業新聞",
                            "data": "News&6"
                        },
                        {
                            "type": "postback",
                            "label": "服務業新聞",
                            "text": "服務業新聞",
                            "data": "News&7"
                        },
                        {
                            "type": "postback",
                            "label": "金融業新聞",
                            "text": "金融業新聞",
                            "data": "News&8"
                        },
                        {
                            "type": "postback",
                            "label": "科技業新聞",
                            "text": "科技業新聞",
                            "data": "News&9"
                        }
                    ]
                )
            )
        )
    
    # 當接收到「履歷推薦」後秀出連結網址 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    user_profile = line_bot_api.get_profile(event.source.user_id)
    if event.message.text == "履歷推薦":
        
        # 將user_id寫入資料庫
        user_id = user_profile.user_id
        
                
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text="http://54.95.77.137:5050/"
        )
    )
        
        conn = connectDB()
        cur = None
        if conn is not None:
            cur = conn.cursor()
            if cur is not None:
                sql = 'INSERT INTO `project`.`line_user_id` (`user_id`) VALUES ("{}")'.format(user_id)
                cur.execute(sql)
                conn.commit()
                
    # 當接收到「推薦結果」後秀出Carousel Template
    if event.message.text == "推薦結果":
        recommend_carousel_template_message = recommend()
        line_bot_api.reply_message(
            event.reply_token,
            recommend_carousel_template_message
        ) 
    

    
# 回傳值事件
save_user = {}
@handler.add(PostbackEvent)
def handle_post_message(event):
    print(event)
    print("==========")
    print(event.postback.data)
    
    # 製造業新聞
    if event.postback.data.split("&")[1] == "6":
        carousel_template_message = get_Manufacturing_news()
        line_bot_api.reply_message(
            event.reply_token,
            carousel_template_message
        )
    
    # 服務業新聞
    if event.postback.data.split("&")[1] == "7":
        carousel_template_message = get_Service_news()
        line_bot_api.reply_message(
            event.reply_token,
            carousel_template_message
        )
    
    # 金融業新聞
    if event.postback.data.split("&")[1] == "8":
        carousel_template_message = get_Financial_news()
        line_bot_api.reply_message(
            event.reply_token,
            carousel_template_message
        )
    
    # 科技業新聞
    if event.postback.data.split("&")[1] == "9":
        carousel_template_message = get_Technology_news()
        line_bot_api.reply_message(
            event.reply_token,
            carousel_template_message
        )
    
    # 當回傳值=new時秀出Flex Message
    if event.postback.data.split("&")[1] == "new":
        new_book_flex_message = new_books()
        line_bot_api.reply_message(
            event.reply_token,
            new_book_flex_message  
        )
    
    # 當回傳值=famous時秀出Flex Message
    if event.postback.data.split("&")[1] == "famous":
        famous_book_flex_message = famous_books()
        line_bot_api.reply_message(
            event.reply_token,
            famous_book_flex_message 
        )
    


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)


# In[ ]:




