from gensim.models.doc2vec import Doc2Vec
import numpy as np
from ckiptagger import WS
import pandas as pd
import re
import random
from datetime import datetime
import os
import logging
import getpass
import time

from flask import Flask, render_template, request, redirect, jsonify, abort,url_for
from flask_bootstrap import Bootstrap
import pymysql
import csv
import pandas as pd
import json
import time

from datetime import datetime
import pytz
def record_now():
    
    utcmoment_naive = datetime.utcnow()
    utcmoment = utcmoment_naive.replace(tzinfo=pytz.utc)

    #print("utcmoment_naive: {0}".format(utcmoment_naive))
    print('-- 紀錄時間戳記 --')
    print("utcmoment:       {0}".format(utcmoment))

    localFormat = "%Y-%m-%d %H:%M:%S"
    timezones = ['America/Los_Angeles', 'Asia/Taipei', 'America/Puerto_Rico']

    localDatetime = utcmoment.astimezone(pytz.timezone('Asia/Taipei'))
    moment=localDatetime.strftime(localFormat)
    return utcmoment_naive

db = pymysql.connect(host='mysql', user='user',password='user',
                           database='project',charset="utf8",port=3306)
#redirect 訪問當前url,重新請求一個新的url,增加使用者體驗

app = Flask(__name__) #__name__代表目前執行的模組
bootstrap = Bootstrap(app) #建立bootstrap物件

# 8/25 update ==
def insert_mysql(password):
    db = pymysql.connect(host='mysql', user='user',password='user',
                           database='project',charset="utf8",port=3306)
    cursor = db.cursor()

    maxm = pd.read_sql("select max(USER) as 'maxm' from Login_2",db)
    user_id=maxm.loc[0,'maxm']+1
    moment=record_now()
    sql_1 = "insert into Login_2(USER, PSW, createDate) values( %s,  '%s', '%s')" % \
            (user_id, password, moment)
    sql_2 = "select * from Login_2 order by USER desc limit 3"
    try:
        cursor.execute(sql_1) # 执行sql语句
        db.commit() # 提交到数据库执行
    except:
        db.rollback() # 如果发生错误则回滚
        print('rollback due to error')
    data = pd.read_sql(sql_2, db) #利用pandas直接获取数据
    print(data)
    db.close()

def insert_recom_3(df):
    db = pymysql.connect(host='mysql', user='user',password='user',
                           database='project',charset="utf8",port=3306)    
    cursor = db.cursor()
    for j in range(3):
        b=[i for i in data.loc[j]]
        print(b[0],b[1],b[2],b[3],b[4],b[5],b[6],b[7],b[8],b[9],b[10])
        sql_1 = "insert into recom_3(Code,companyName,jobName,salary,C,longitude,latitude,Similarity) \
        values( '%s','%s','%s','%s','%s', %s,%s,%s)" % (b[1],b[2],b[3],b[4],b[5],b[6],b[7],b[8])

        try:
            cursor.execute(sql_1) # 执行sql语句
            db.commit() # 提交到数据库执行
            print('success')
        except:
            db.rollback() # 如果发生错误则回滚
            print('error on %s' % j)
    
    
#取得資訊的時候GET
#送出資訊的時候POST

@app.route('/',methods=['POST','GET'])#利用methods來設置這個路由允許的方式,如果沒有設置POST那使用者點擊之後會有異常訊息告知該路由不支援pOST
def show_resume():
    #print('hello')
    if request.method =='POST':#利用request來不捉使用者端的動作是否為POST,如果是POST就代表使用者端透過submit所提交過來的資料
        req = request.form
        #resume = req['resume']
        print('-- 接收POST封包內容 --')
        print(req)
        #print(type(req)) #查看型別
        #print(dir(req))  #dir用來尋找一個物件的所有屬性
        mystr=req.get("resumecatcher")
        #print("this's what i want:{}".format(mystr))
        insert_mysql(mystr) #結果存到mysql 8/25 ==laurent
        
        # 調用 recommend.py 
        print('履歷輸入字串長度: {}'.format(len(mystr)))
        with open('/home/spades/project/spades/Vincent/Job_Recommendation_0828_report.py','r') as f:
            exec(f.read())
        
        # ==laurent
        
        #return  redirect(request.url)

        #model = doc2vec.Doc2vec.load('Doc2Vec_104_jobs.model')
    return render_template('resume.html')

@app.route('/index')
def my_index():
    return render_template('index.html')

@app.route('/index/new')
def new_data():
    return render_template('new.html')

@app.route('/index/new/third')
def third_job():
    return render_template('third.html')

@app.route('/index/new/third/map', methods=["GET", "POST"])
def google_map():

   if request.method == "GET":
      args = request.args
   jobCode = args["jobCode"]

   sql_2 = "select * from recom_2 where Code = '{}'".format(jobCode)
   data = pd.read_sql(sql_2, db)  # 利用pandas直接獲取數據

   job = data[data["Code"] == jobCode]
   t1, t2, t3 = '', '', ''
   if job.shape[0] == 0:
       print("No Job Found")
   else:
       t1 = job.iloc[0]["Code"]
       t2 = job.iloc[0]["longitude"]
       t3 = job.iloc[0]["latitude"]
       print(f"Code: {t1},\nLong: {t2},\nLat: {t3}")
   return render_template('map.html',jobcode = t1, lat = t3, lon = t2)


@app.route('/index/new/third/map/recommend',methods=['GET','POST'])
def recommend():
    #建立連線 conn是一個連結器
    db = pymysql.connect(host='mysql', user='user',password='user',
                           database='project',charset="utf8",port=3306)
    cursor = db.cursor()
    sql_2 = "select id, Code, companyName, jobName, salary, C , Similarity from recom_2 order by id desc limit 30"
    # analysisUrl = C
    data = pd.read_sql(sql_2, db)  # 利用pandas直接获取数据
    data.sort_values(by='Similarity',ascending=False,inplace=True)
    data.drop(['Similarity'], axis=1, inplace=True)
    
    datarows = list()
    for jobs in data.values:
        job_list = list()
        for item in jobs:
            job_list.append(item)

        datarows.append(job_list)

    colnames = ['jobCode', 'custName', 'jobName', 'salary', 'url','map', 'like']
    df_result = pd.DataFrame(columns=colnames)


    # for ids in model:
    #     if df_result.shape[0] == 0:
    #         df_result = df[df["jobCode"] == ids]
    #     else:
    #         df_result = df_result.append(df[df["jobCode"] == ids])
    # datarows = df_result.values.tolist()
    # print(datarows)

    #if request.method == 'POST':  # 利用request來不捉使用者端的動作是否為POST,如果是POST就代表使用者端透過submit所提交過來的資料
    return render_template('recommend.html',colnames=colnames,datarows=datarows)

import random
def random_3(source_list):
    code_list=[]
    while len(code_list)<3:
        a=random.choice(source_list)
        if a not in code_list:
            code_list.append(a)
    return code_list

@app.route('/index/new/third/map/recommend/recommend_2',methods=['GET','POST'])
def recommend_2():
    db = pymysql.connect(host='mysql', user='user',password='user',
                           database='project',charset="utf8",port=3306) 
    '''
    sql_2 = "select id from recom_2"
    data = pd.read_sql(sql_2, db)
    a=data['id'].tolist()
    id_list=random_3(a)
    print('--final 3 recom_id--',id_list)

    db = pymysql.connect(host='mysql', user='user',password='user',
                           database='project',charset="utf8",port=3306)
    sql_2 = "select * from recom_2 where id in ({})".format(id_list).replace('[','').replace(']','')
    data = pd.read_sql(sql_2, db)
    print('check',data)
    insert_recom_3(data)
    '''
    sql_2 = "select id, Code, companyName, jobName, salary, C from project.recom_2 order by id desc limit 3"
    data = pd.read_sql(sql_2, db)  # 利用pandas直接获取数据

    datarows_1 = list()
    for jobs_1 in data.values:  # 取出裡面所有的值
        job_list_1 = list()
        for item in jobs_1:
            job_list_1.append(item)

        datarows_1.append(job_list_1)

    colnames_1 = ['jobCode', 'custName', 'jobName', 'salary', 'url', 'map']
    df_result = pd.DataFrame(columns=colnames_1)

    return render_template('recommend_2.html', colnames=colnames_1, datarows=datarows_1)

@app.route('/update', methods=['GET', 'POST'])
def like():

    args = ''
    if request.method == 'POST':
        args = request.form.getlist("chk[]")  #getlist取一鍵多值類型的參數
        # print(f"FORM: {request.form}")
        # print(f"ARGS: {args}")

    json = {}
    json["jobs"] = []
    json["msg"] = "test"

    if str(args) != "NoneType" and len(args) >= 1:
        for jobs in args:
            job = {}
            job_list = eval(jobs)
            print(f"JOB: {job_list}")
            job["id"] = job_list[0]
            job["job"]=job_list[1]
            job["name"] = job_list[2]
            job["salary"] = job_list[3]

            json["jobs"].append(job)
        json["msg"] = "success"
    else:
        json["msg"] = "no jobCodes"
    # t=request.args['id']
    #t4=request.args['jobName']
    print(f"JSON: {json}")

    return render_template('update.html', json=json)



@app.errorhandler(404)  #錯誤處理(找不到頁面)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500) #錯誤處理(系統內部錯誤)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__': #如果以主程式執行
    app.run(host="0.0.0.0",port=5050) #立刻啟動伺服器
