#coding:utf-8
'''获取关注的用户的新微博，并发出告警'''
import urllib
import urllib2
import traceback
import json
import sys
import io
import time
import winsound
import random

reload(sys)
sys.setdefaultencoding("utf-8")

class UnicodeStreamFilter:  
    def __init__(self, target):  
        self.target = target  
        self.encoding = 'utf-8'  
        self.errors = 'replace'  
        self.encode_to = self.target.encoding  
    def write(self, s):  
        if type(s) == str:  
            s = s.decode("utf-8")  
        s = s.encode(self.encode_to, self.errors).decode(self.encode_to)  
        self.target.write(s)  
          
if sys.stdout.encoding == 'cp936':  
    sys.stdout = UnicodeStreamFilter(sys.stdout) 

#应用申请的APPKEY及APPSECRETE
APPKEY = ""
APPSECRETE = ""
#用户授权的code
CODE = ""
REDIRECTURI = ""
#使用authorized方法打印出的ACCESSTOKEN
ACCESSTOKEN = ""

#微博id
UID = ""
NICKNAME = ""

#是否程序是第一次启动
first = True

content_dict = dict()

def post_data(url, datas):
    '''发送post请求'''
    req = urllib2.Request(url) 
    datas = urllib.urlencode(datas) 
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor()) 
    response = opener.open(req, datas) 
    return response.read() 

def authorized():
    '''获取用户授权token'''
    cururl = "https://api.weibo.com/oauth2/access_token"
    datas = {
        "client_id": APPKEY,
        "client_secret": APPSECRETE,
        "grant_type": "authorization_code",
        "code": CODE,
        "redirect_uri": REDIRECTURI
    }
    content = post_data(cururl, datas)
    return json.loads(content)

def get_new_info():
    '''获取最新的微博消息'''
    cururl = "https://api.weibo.com/2/statuses/home_timeline.json"
    datas = {
        "access_token": ACCESSTOKEN
    }
    cururl = cururl + "?" + urllib.urlencode(datas)
    content = urllib.urlopen(cururl).read()
    return json.loads(content)

def leave_comment(itemid):
    '''发布留言评论'''
    comment_list = ["爱你，么么哒","你永远是我心中的小仙女","永远支持你","爱你，比个heart"]
    #随机一条评论
    curcomment = "替主人对你说："+comment_list[random.randint(0,len(comment_list)-1)]
    cururl = "https://api.weibo.com/2/comments/create.json"
    datas = {
        "access_token": ACCESSTOKEN,
        "comment": curcomment,
        "id": str(itemid)
    }
    post_data(cururl, datas)
    print "替主人给最爱的 ",NICKNAME," 留了一条评论，内容为："
    print curcomment

def read_new_content():
    '''读取最新的微博内容'''
    global first
    
    content = get_new_info()
    has_new = False
    index = -1
    for item in content["statuses"]:
        if str(item["user"]["id"]) == UID:
            if item["id"] not in content_dict.keys():
                index = index + 1
                has_new = True
                print "你最爱的 ",NICKNAME," 于 ",str(item["created_at"])," 发布了新微博："
                print
                print str(item["text"]).decode("utf-8")
                content_dict[item["id"]] = {
                    "date":str(item["created_at"]),
                    "text:":str(item["text"]).decode("utf-8")
                }
                if (first and index == 0) or not first:
                    leave_comment(item["id"])
                print "**********************************************"
                print
    first = False
    return has_new

def run():
    while True:
        curtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        print curtime
        print "主人，我对于微博进行了一次访问"
        has_new = read_new_content()
        if not has_new:
            print "抱歉，你最爱的 ",NICKNAME," 当前未更新微博"
        else:
            #微博有更新，发出10秒的告警
            winsound.Beep(600,1000)
        print
        #每10分钟检测一次微博
        time.sleep(600)

if __name__ == '__main__':
    # content = authorized()
    # print content["access_token"]
    run()
