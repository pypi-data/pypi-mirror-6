#!/usr/bin/python
# -*- coding: utf-8 -*-  

import urllib2
import urllib
import json
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
 
 # 在 urllib2 上注册 http 流处理句柄
register_openers()

import hashlib
import time
from WeixinException import * 

class ErrorCode(object):
    TokenExpire = 42001

class Const(object):
    api_host = "https://api.weixin.qq.com"
    media_host = "http://file.api.weixin.qq.com"
    qrcode_host = "https://mp.weixin.qq.com"
    appid = "wxdd82d38cee1fe6e6"
    secret = "b8d5dcb4ab2e5d2ab891a1cbc62bca83"

class Request(object):
    
    def __init__(self,token,host):
        self.host = host
        self.token = token

    def get_host(self):
        return self.host

    def get_token(self):
        return self.token

    def get_tokenid(self):
        return self.token.get()

    def request(self,url,params,data={},method='GET',headers={'Content-Type': 'application/json'},times=2,sleep_second=1):
        errormsg = {}
        while times:
            try:
                response = self._request(url,params,data,method,headers)
                if response.has_key("errcode") and response["errcode"] == ErrorCode.TokenExpire:
                    self.token.refresh()
                    errormsg = response
                return response
            except Exception,e:
                errormsg = e
            time.sleep(sleep_second)
            times = times - 1
        raise WeixinException({"errormsg":errormsg})

    def _request(self,url,params,data,method,headers):
        url = '%s%s?%s' % (self.host,url,urllib.urlencode(params))
        if method == 'GET':
            response = urllib2.urlopen(url).read()
        elif method == 'POST':
            req = urllib2.Request(url, data, headers)
            response = urllib2.urlopen(req).read()
        return response

class MediaRequest(Request):
    
    def __init__(self,token,host=Const.media_host):
        super(MediaRequest,self).__init__(token,host) 

    def _request(self,url,params,data,method,headers):
        url = '%s%s?%s' % (self.host,url,urllib.urlencode(params))
        if method == 'GET':
            f = urllib2.urlopen(url)
            with open(data["filepath"], "wb") as local_file:
                local_file.write(f.read())
            return {"status":"success"}
        elif method == 'POST':
            datagen, headers = multipart_encode({params["type"]: open(data["filepath"], "rb")})
            request = urllib2.Request(url, datagen, headers)
            response = urllib2.urlopen(request).read()
            response = json.loads(response)
            return response

class QrcodeRequest(MediaRequest):
    def __init__(self,token,host=Const.qrcode_host):
        super(QrcodeRequest,self).__init__(token,host)
            

class APIRequest(Request):

    def __init__(self,token,host=Const.api_host):
        super(APIRequest,self).__init__(token,host)

    def _request(self,url,params,data,method,headers):
        data = json.dumps(data,ensure_ascii=False)
        response = super(APIRequest,self)._request(url,params,data,method,headers)
        response = json.loads(response)
        return response


class TokenRequest(APIRequest):

    def __init__(self,host=Const.api_host):
        super(TokenRequest,self).__init__(None,host)

    def request(self,url,params,data={},method='GET',headers={'Content-Type': 'application/json'},times=2,sleep_second=1):
        errormsg = {}
        while times:
            try:
                response = self._request(url,params,data,method,headers)
                if response.has_key("access_token"):
                    return response
                else:
                    errormsg = response
            except Exception,e:
                errormsg = e
            time.sleep(sleep_second)
            times = times - 1

        raise WeixinException({"errormsg":errormsg})


class Token(object):

    tokenid = None
    def __init__(self,request,appid=Const.appid,secret=Const.secret):
        self.request = request
        self.appid = appid
        self.secret = secret

    def get(self):
        if self.__class__.tokenid == None:
            self.__class__.tokenid = self._create()
        return self.__class__.tokenid

    def refresh(self):
        response = self._create()
        self.__class__.tokenid = response["access_token"]
        return self.__class__.tokenid

    #https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
    def _create(self):
        params = {
            "grant_type" : "client_credential",
            "appid" : self.appid,
            "secret" : self.secret
        }
        response = self.request.request("/cgi-bin/token",params)
        return response["access_token"]


class Qrcode(object):

    def __init__(self,request):
        self.request = request

    def show(self,ticket,filepath):
        url = "/cgi-bin/showqrcode"
        params = {"ticket": ticket}
        data = {"filepath":filepath}
        r = self.request.request(url,params,data)
        print(r)


class WeixinMedia(object):

    def __init__(self,request):
        self.request = request

    #http://file.api.weixin.qq.com/cgi-bin/media/upload?access_token=ACCESS_TOKEN&type=TYPE
    def upload_media(self,media_type,media):
        url = "/cgi-bin/media/upload"
        params = {
            "access_token" : self.request.get_tokenid(),
            "type" : media_type
        }
        data = {
            "filepath" : media
        }
        r = self.request.request(url,params,data,method='POST')
        return r

    #http://file.api.weixin.qq.com/cgi-bin/media/get?access_token=ACCESS_TOKEN&media_id=MEDIA_ID
    def get_media(self,media_id,filepath):
        url = "/cgi-bin/media/get"
        params = {
            "access_token" : self.request.get_tokenid(),
            "media_id" : media_id
        }
        data = {
            "filepath" : filepath
        }
        r = self.request.request(url,params,data,method='GET')
        print(r)

class Weixin(object):

    def __init__(self,request):
        self.request = request

    def check_signature(self,token,signature,timestamp,nonce,echostr):
        tmplist = [token,timestamp,nonce]
        tmplist.sort()
        sha1 = hashlib.sha1()
        map(sha1.update,tmplist)
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            return echostr
        else:
            raise WeixinException({"errormsg":"check_signature failed"})

    def xml2dict(self,message):
        obj = XML2Dict()
        return obj.parse(message)

    def dict2xml(self,message):
        obj = Dict2XML()
        return obj.parse(message)

    '''
    {
        "touser":"OPENID",
        "msgtype":"text",
        "text":
        {
             "content":"Hello World"
        }
    }
    '''
    def send_custom_message(self,message):
        url = "/cgi-bin/message/custom/send"
        params = {"access_token" : self.request.get_tokenid()}
        response = self.request.request(url,params,message,'POST')
        print(response)

    '''
    {"group":{"name":"test"}}
    '''
    def create_group(self,group):
        url = "/cgi-bin/groups/create"
        params = {"access_token" : self.request.get_tokenid()}
        response = self.request.request(url,params,group,'POST')
        if response.has_key("group"):
            return response
        else:
            raise WeixinException(response)

    #https://api.weixin.qq.com/cgi-bin/groups/get?access_token=ACCESS_TOKEN
    def get_group(self):
        url = "/cgi-bin/groups/get"
        params = {"access_token" : self.request.get_tokenid()}
        response = self.request.request(url,params)
        if response.has_key("groups"):
            return response
        else:
            raise WeixinException(response)

    #https://api.weixin.qq.com/cgi-bin/user/info?access_token=ACCESS_TOKEN&openid=OPENID&lang=zh_CN
    def get_user_info(self,openid,lang="zh_CN"):
        url = "/cgi-bin/user/info"
        params = {
            "access_token" : self.request.get_tokenid(),
            "openid" : openid,
            "lang" : lang
        }
        response = self.request.request(url,params)
        if response.has_key("errcode"):
            raise WeixinException(response)
        else:
            return response

    #https://api.weixin.qq.com/cgi-bin/user/get?access_token=ACCESS_TOKEN&next_openid=NEXT_OPENID
    def get_follow_users(self,next_openid=""):
        url = "/cgi-bin/user/get"
        params = {
            "access_token" : self.request.get_tokenid(),
            "next_openid" : next_openid
        }
        response = self.request.request(url,params)
        if response.has_key("errcode"):
            raise WeixinException(response)
        else:
            return response

    
    '''
    {"openid":"od8XIjsmk6QdVTETa9jLtGWA6KBc"}
    '''
    def get_groupid_by_openid(self,openid):
        url = "/cgi-bin/groups/getid"
        params = {"access_token" : self.request.get_tokenid()}
        response = self.request.request(url,params,openid,'POST')
        if response.has_key('groupid'):
            return response
        else:
            raise WeixinException(response)

    #https://api.weixin.qq.com/cgi-bin/groups/update?access_token=ACCESS_TOKEN
    '''
    {"group":{"id":108,"name":"test2_modify2"}}
    '''
    def update_group(self,group):
        url = "/cgi-bin/groups/update"
        params = {"access_token" : self.request.get_tokenid()}
        response = self.request.request(url,params,group,'POST')
        if response['errcode'] == 0:
            return response
        else:
            raise WeixinException(response)

    #https://api.weixin.qq.com/cgi-bin/groups/members/update?access_token=ACCESS_TOKEN
    '''
    {"openid":"oDF3iYx0ro3_7jD4HFRDfrjdCM58","to_groupid":108}
    '''
    def update_group_member(self,member):
        url = "/cgi-bin/groups/members/update"
        params = {"access_token" : self.request.get_tokenid()}
        response = self.request.request(url,params,member,'POST')
        if response['errcode'] == 0:
            return response
        else:
            raise WeixinException(response)

    #https://api.weixin.qq.com/cgi-bin/menu/create?access_token=ACCESS_TOKEN
    '''
    {
     "button":[
     {  
          "type":"click",
          "name":"今日歌曲",
          "key":"V1001_TODAY_MUSIC"
      },
      {
           "type":"click",
           "name":"歌手简介",
           "key":"V1001_TODAY_SINGER"
      },
      {
           "name":"菜单",
           "sub_button":[
           {    
               "type":"view",
               "name":"搜索",
               "url":"http://www.soso.com/"
            },
            {
               "type":"view",
               "name":"视频",
               "url":"http://v.qq.com/"
            },
            {
               "type":"click",
               "name":"赞一下我们",
               "key":"V1001_GOOD"
            }]
       }]
    }
    '''
    def create_menu(self,menu):
        url = "/cgi-bin/menu/create"
        params = {"access_token" : self.request.get_tokenid()}
        response = self.request.request(url,params,menu,'POST')
        if response['errcode'] == 0:
            return response
        else:
            raise WeixinException(response)

    #https://api.weixin.qq.com/cgi-bin/menu/get?access_token=ACCESS_TOKEN

    def get_menu(self):
        url = "/cgi-bin/menu/get"
        params = {"access_token" : self.request.get_tokenid()}
        response = self.request.request(url,params)
        if response.has_key("menu"):
            return response
        else:
            raise WeixinException(response)

    #https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=ACCESS_TOKEN
    def delete_menu(self):
        url = "/cgi-bin/menu/delete"
        params = {"access_token" : self.request.get_tokenid()}
        response = self.request.request(url,params)
        if response['errcode'] == 0:
            return response
        else:
            raise WeixinException(response)

    #https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=TOKEN
    '''
    {"expire_seconds": 1800, "action_name": "QR_SCENE", "action_info": {"scene": {"scene_id": 123}}}
    {"action_name": "QR_LIMIT_SCENE", "action_info": {"scene": {"scene_id": 123}}}
    '''
    def create_qrcode(self,qrcode):
        url = "/cgi-bin/qrcode/create"
        params = {"access_token" : self.request.get_tokenid()}
        response = self.request.request(url,params,qrcode,'POST')
        if response.has_key("ticket"):
            return response
        else:
            raise WeixinException(response)


if __name__ == '__main__':

    token_req = TokenRequest()
    token = Token(token_req)
    api_req = APIRequest(token)
    wx = Weixin(api_req)
    #https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
    #wx.get_token()
   # print(wx.token)
