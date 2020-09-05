#!/usr/bin/env python
# coding: utf-8

# In[56]:


#!/usr/bin/env python
# coding: utf-8

#import sys
from gensim.models.doc2vec import Doc2Vec
import numpy as np
from ckiptagger import WS
import pandas as pd
import re
import random
from datetime import datetime
import os
import logging
#from LinkedIn import linkedin_crawler
import getpass
import pymysql
import pandas as pd
import time


def recommend():
    #模型讀取
    model = Doc2Vec.load("/home/spades/project/spades/Vincent/Doc2Vec_0826_v300_m1_e200_w3.model")

    #CKIP斷詞資料
    #os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"
    #ws = WS('data', disable_cuda=False)
    ws = WS('/home/spades/project/spades/Vincent/data') #有使用GPU / Tensorflow-GPU再註解掉這行，啟用上面兩行


    #print("--- %s seconds ---" % (time.time() - start_time))
    # updated 8/25 ==
    def query_mysql():
        db = pymysql.connect(host='mysql', user='user',password='user',
                               database='project',charset="utf8",port=3306)
        cursor = db.cursor()

        maxm = pd.read_sql("select max(USER) as 'maxm' from Login_2",db)
        q=maxm.loc[0,'maxm']
        sql_2 = "select * from Login_2 where USER={}".format(q) 

        data = pd.read_sql(sql_2, db) #利用pandas直接获取数据
        data = data.loc[0,'PSW']
        db.close()
        return data

    def insert_recom2(a_list):   
        db = pymysql.connect(host='mysql', user='user',password='user',
                               database='project',charset="utf8",port=3306)
        cursor = db.cursor()

        # colect 30

        code_list = [i[0] for i in a_list]
        print('1',code_list)
        sql_2 = "select distinct Code, companyName, jobName, salary, C, longitude, latitude from s104_full where Code in ({})".format(code_list).replace('[','').replace(']','')
        data = pd.read_sql(sql_2, db) #利用pandas直接获取数据
        data.insert(7,'Similarity',0)
        print('2',data)
        data_code_list = data['Code'].tolist()
        data = data.set_index('Code')
        
        for info in a_list:
            if info[0] in data_code_list:
                data.loc[info[0],'Similarity'] = info[1]
        data = data.reset_index()
        df = data
        print('--prepared to insert--',df)
        #print("--- %s seconds ---" % (time.time() - start_time))
        # insert 30
        for i in range(0,30):
            if i < df.shape[0]:
                C1=df.loc[i]['Code']
                C2=df.loc[i]['companyName']
                C3=df.loc[i]['jobName']
                C4=df.loc[i]['salary'] 
                C5=df.loc[i]['C'] 
                C6=df.loc[i]['longitude'] 
                C7=df.loc[i]['latitude']
                C8=df.loc[i]['Similarity']
            else:
                C1=""
                C2=""
                C3=""
                C4=""
                C5=""
                C6=0
                C7=0
                C8=0

            sql_1 = "insert into recom_2(Code, companyName, jobName, salary, C, longitude, latitude, Similarity) values('%s','%s','%s','%s','%s', %s ,%s ,%s)" %                     (C1,C2,C3,C4,C5,C6,C7,C8)

            try:
                cursor.execute(sql_1) # 执行sql语句
                db.commit() # 提交到数据库执行
            except:
                db.rollback() # 如果发生错误则回滚
                print('rollback due to error')
        db.close()
        #print("--- %s seconds ---" % (time.time() - start_time))
    # 8/25 end ==

    #消除符號
    def regularize_(target):
        #return re.sub("[0-9【】◎★/◆※⦿\%\[\]\-\"\“\”\(\)（）{}\'=●▲▼《》○]", "", target).replace('\r',' ').replace('\n',' ')
        ##Vincent改 - 斷詞結構改一下
        return re.sub("[【】◎★/◆※⦿\%\[\]\-\"\“\”\(\)（）{}\'=●▲▼.〈〉《》○?？!，。！，,:　：~.、；_／ ]", "★", target).replace('\r','★').replace('\n','★')
    #定義斷詞功能_這邊是改版給單句用的
    def word_seg(sentence_list): #輸入包含多斷文章(句子)的list
        sepped = ws([sentence_list],
                    sentence_segmentation=True,
                    #segment_delimiter_set={'?', '？', '!', '！', '。', ',','，', ';', ':', '、','：','\\n','\\r','.',' ','_'})
                    ##Vincent改 - 斷詞結構改一下2
                    segment_delimiter_set={'\\n','\\r','.',' ','_','★'})
        return sepped[0]

    #比較兩個斷詞組的相似性
    def compare_similarity(p1, p2):
        d2v_similarity = np.dot(model.infer_vector(p1), model.infer_vector(p2)) / (np.linalg.norm(model.infer_vector(p1))*np.linalg.norm(model.infer_vector(p2)))
        return d2v_similarity


    doc_origin = query_mysql() # == amend 08/25

    #目標履歷去雜質、斷字斷詞
    doc = regularize_(doc_origin)
    doc = word_seg(doc)

    #輸出目標履歷資料
    print('履歷內容： %s' % (doc_origin))
    print('--------------------------------------------')

    #套用模型到目標履歷詞組
    inferred_vector = model.infer_vector(doc)
    #取得以相似度排列的職缺list
    sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))

    #輸出推薦 # == amend 08/25
    a_list=[]
    for index in range(0,30):
        #a_list.append(sims[index][0])
        a_list.append(sims[index])
    print('------------in mySQLdb------------------',a_list)
    insert_recom2(a_list)

    

if __name__ == '__main__': #如果以主程式執行
    recommend() #立刻啟動伺服器
    
    

