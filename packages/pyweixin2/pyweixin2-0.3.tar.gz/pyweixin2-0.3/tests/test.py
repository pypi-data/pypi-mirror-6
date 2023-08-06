#!/usr/bin/python
# -*- coding: utf-8 -*-  

from pyweixin2.Weixin import * 
import unittest

'''
assertEqual(a, b)       a == b   
assertNotEqual(a, b)    a != b   
assertTrue(x)   bool(x) is True  
assertFalse(x)  bool(x) is False         
assertIs(a, b)  a is b  2.7
assertIsNot(a, b)       a is not b      2.7
assertIsNone(x) x is None       2.7
assertIsNotNone(x)      x is not None   2.7
assertIn(a, b)  a in b  2.7
assertNotIn(a, b)       a not in b      2.7
assertIsInstance(a, b)  isinstance(a, b)        2.7
assertNotIsInstance(a, b)       not isinstance(a, b)    2.7


assertAlmostEqual(a, b) round(a-b, 7) == 0       
assertNotAlmostEqual(a, b)      round(a-b, 7) != 0       
assertGreater(a, b)     a > b   2.7
assertGreaterEqual(a, b)        a >= b  2.7
assertLess(a, b)        a < b   2.7
assertLessEqual(a, b)   a <= b  2.7
assertRegexpMatches(s, r)       r.search(s)     2.7
assertNotRegexpMatches(s, r)    not r.search(s) 2.7
assertItemsEqual(a, b)  sorted(a) == sorted(b) and works with unhashable objs   2.7
assertDictContainsSubset(a, b)  all the key/value pairs in a exist in b 2.7

assertRaises(exc, fun, *args, **kwds)   fun(*args, **kwds) raises exc    
assertRaisesRegexp(exc, r, fun, *args, **kwds)  fun(*args, **kwds) raises exc and the message matches regex r   2.7

    def __init__(self,host,appid="",secret=""):
    def get_token(self):
    def _refresh_token(self):
    def _create_token(self):
    def check_signature(self,token,signature,timestamp,nonce,echostr):
    def xml2dict(self,message):
    def dict2xml(self,message):
    def send_custom_message(self,message):
    def create_group(self,group):
    def get_group(self):
    def get_user_info(self,openid,lang="zh_CN"):
    def get_follow_users(self,next_openid=""):
    def get_groupid_by_openid(self,openid):
    def update_group(self,group):
    def update_group_member(self,member):
    def create_menu(self,menu):
    def get_menu(self):
    def delete_menu(self):
    def create_qrcode(self,qrcode):
    def show_qrcode(self,ticket):
    def json_request(self,url,params={},data={},method='GET',times=3,sleep_second=5):
    def request(self,url,params={},data={},method='GET'):

'''


class WeixinTestCase(unittest.TestCase):
    def setUp(self):

        token_req = TokenRequest()
        token = Token(token_req)

        qr_req = QrcodeRequest(token)
        self.qrcode = Qrcode(qr_req)
        
        media_req = MediaRequest(token)
        self.wxm = WeixinMedia(media_req)

        api_req = APIRequest(token)
        self.wx = Weixin(api_req)
        #brave story    oi28wt2sUiKI4kFFAu45Flo-vybI
        self.openid = "oi28wt2sUiKI4kFFAu45Flo-vybI"
        #self.wx.token = "9BT7tXbxmswlFIPeoOrQk-w8z6L0bgFY23s2h3PGyaJM_4oGrcMmqUcoUG5hTL3nihqsaeXIrQQ1I6KYRrLl8I1kfHubY7qMQDdpXcZPWH1Ainc_4OHdzLUbnYtgEQ3oqeegKl4V0tw0-qdimzHW0Q"

    def tearDown(self):
        self.wx = None

    def testGetToken(self):
        response = self.wx.get_token()
    
    def testSendCustomMessage(self):

        message = {
            "touser" : self.openid,
            "msgtype":"text",
            "text": {
                "content":"我我"
            }
        }
        self.wx.send_custom_message(message)   

    def testCreateGroup(self):
        group = {"group":{"name":"test"}}
        self.wx.create_group(group)
        group = {"group":{"name":"test1"}}
        self.wx.create_group(group)

    def testGetGroup(self):
        self.wx.get_group()

    def testGetGroupidByOpenid(self):
        openid = {"openid":self.openid}
        self.wx.get_groupid_by_openid(openid)

    def testUpdateGroup(self):
        
        gps = self.wx.get_group()
        for g in gps["groups"]:
            group = {"group":{"id":g['id'],"name":"test2_modify2"}}
            self.wx.update_group(group)
        #group = {"group":{"id":108,"name":"test2_modify2"}}
        #self.wx.update_group(group)

    def testUpdateGroupMember(self):
        gps = self.wx.get_group()
        for g in gps["groups"]:
            member = {"openid":"oDF3iYx0ro3_7jD4HFRDfrjdCM58","to_groupid":g['id']}
            self.wx.update_group_member(member)
        #member = {"openid":"oDF3iYx0ro3_7jD4HFRDfrjdCM58","to_groupid":108}
        #self.wx.update_group_member(member)

    def testCreateMenu(self):
        menu = {
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

        self.wx.create_menu(menu)

    def testGetMenu(self):
        self.wx.get_menu()

    def testDeleteMenu(self):
        self.wx.delete_menu()

    def testCreateQrcode(self):
        
        qrcode = {"expire_seconds": 1800, "action_name": "QR_SCENE", "action_info": {"scene": {"scene_id": 123}}}

        r = self.wx.create_qrcode(qrcode)
        print(r)
        qrcode = {"action_name": "QR_LIMIT_SCENE", "action_info": {"scene": {"scene_id": 123}}}
        r = self.wx.create_qrcode(qrcode)
        print(r)

    def testShowQrcode(self):
        qrcode = {"expire_seconds": 1800, "action_name": "QR_SCENE", "action_info": {"scene": {"scene_id": 123}}}
        r = self.wx.create_qrcode(qrcode)
        self.qrcode.show(r['ticket'],'qrcode1.jpg')

        qrcode = {"action_name": "QR_LIMIT_SCENE", "action_info": {"scene": {"scene_id": 123}}}
        r = self.wx.create_qrcode(qrcode)
        self.qrcode.show(r['ticket'],'qrcode2.jpg')
    
    def testGetUserInfo(self):
        openid = self.openid
        self.wx.get_user_info(openid)

    def testGetFollowUsers(self):
        self.wx.get_follow_users()

    def testUploadMedia(self):
        r = self.wxm.upload_media('image',"qrcode.jpg")
        print(r)

    def testGetMedia(self):
        r = self.wxm.upload_media('image',"qrcode.jpg")
        r = self.wxm.get_media(r['media_id'],'o.jpg')
        #media_id
        #self.wx.get_media()

    def testXML2JSON(self):
        message = '''
        <xml>
        <ToUserName><![CDATA[toUser]]></ToUserName>
        <FromUserName><![CDATA[FromUser]]></FromUserName>
        <CreateTime>123456789</CreateTime>
        <MsgType><![CDATA[event]]></MsgType>
        <Event><![CDATA[subscribe]]></Event>
        </xml>
        '''
        print(self.wx.to_json(message))

    def testJSON2XML(self):
        message = {'MsgType': 'event', 'FromUserName': 'FromUser', 'ToUserName': 'toUser', 'Event': 'subscribe', 'CreateTime': 123456789L}
        print(self.wx.to_xml(message))

def suite():
    suite = unittest.TestSuite()
    #suite.addTest(WeixinTestCase('testUploadMedia'))
    #suite.addTest(WeixinTestCase('testSendCustomMessage'))
    #suite.addTest(WeixinTestCase('testCreateGroup'))
    #suite.addTest(WeixinTestCase('testGetGroup'))
    #suite.addTest(WeixinTestCase('testGetGroupidByOpenid'))
    #suite.addTest(WeixinTestCase('testUpdateGroup'))
    #suite.addTest(WeixinTestCase('testUpdateGroupMember'))
    #suite.addTest(WeixinTestCase('testCreateMenu'))
    #suite.addTest(WeixinTestCase('testGetMenu'))
    #suite.addTest(WeixinTestCase('testDeleteMenu'))
    #suite.addTest(WeixinTestCase('testCreateQrcode'))
    #suite.addTest(WeixinTestCase('testGetUserInfo'))
    #suite.addTest(WeixinTestCase('testGetFollowUsers'))
    #suite.addTest(WeixinTestCase('testShowQrcode'))
    #suite.addTest(WeixinTestCase('testUploadMedia'))
    #suite.addTest(WeixinTestCase('testGetMedia'))
    suite.addTest(WeixinTestCase('testXML2JSON'))
    suite.addTest(WeixinTestCase('testJSON2XML'))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest = 'suite')
