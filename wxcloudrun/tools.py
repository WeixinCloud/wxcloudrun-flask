#!/usr/bin/python3
import hashlib
import os
import json
import time
import requests
from hashlib import md5


class ToodoWechatException(Exception):
    pass


def checkError(reqJson):
    """
    检测返回的json消息中是否有错误信息，如果有抛出错误，否则返回json信息
    :param reqJson: 返回的json数据
    :return: 如果有抛出错误，否则返回json信息
    """
    if "errcode" in reqJson and reqJson['errcode'] != 0:
        raise ToodoWechatException(
            f"{reqJson} 详细错误信息对比文档：https://developers.weixin.qq.com/doc/oplatform/Return_codes/Return_code_descriptions_new.html")
    return reqJson


class WechatMP:
    """
    本接口适用于个人订阅号，加密类型支持明文模式和兼容模式
    功能列表：
        1、获取access_token
        2、获取微信服务器IP地址
        3、验证消息真实性
        4、接收普通消息（包括语音识别结果，需要在公众号后台 开发->接口权限 中手动开启）
        5、接收事件推送
        6、自动回复
        7、永久素材管理
    网页服务尚未开发，仅包含功能服务
    """
    def __init__(self, Token, appId, secret, encodingAESKey=None):
        self.Token = Token
        self.appId = appId
        self.secret = secret
        self.encodingAESKey = encodingAESKey
        self.basePath = os.path.dirname(__file__)
        self._session = requests.Session()
        self.tokenCache = md5(f"{self.appId}{self.secret}".encode()).hexdigest() + '.json'

    def _requests(self, method, url, decode_level=2, retry=10, timeout=15, **kwargs):
        if method in ["get", "post"]:
            for _ in range(retry):
                try:
                    response = getattr(self._session, method)(url, timeout=timeout, **kwargs)
                    return response.json() if decode_level == 2 else response.content if decode_level == 1 else response
                except Exception as e:
                    print(e)
                    print(f"[{_ + 1} / {retry}]网络请求失败正在重新尝试：method: {method}; url: {url}")
        raise ToodoWechatException(f"网络请求失败，请检查您的网络连接")

    def getNewToken(self):
        """
        从服务器获取新的access_token
        文件缓存token格式：{"access_token":"ACCESS_TOKEN","expires_in":7200,"expires_at": int}
        :return: access_token
        """
        baseUrl = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appId}&secret={self.secret}"
        res = checkError(self._requests('get', baseUrl))
        res['expires_at'] = int(time.time()) + res['expires_in']
        with open(os.path.join(self.basePath, self.tokenCache), 'w') as f:
            f.write(json.dumps(res))
        return res['access_token']

    def getToken(self):
        """
        检测token是否过期，未过期直接返回，如果过期则生成新的access_token并返回
        如果脚本长时间运行，每次使用token前进行token检测是必须的
        文件缓存token格式：{"access_token":"ACCESS_TOKEN","expires_in":7200,"expires_at": int}
        :return: access_token
        """
        # 首次打开，没有缓存文件的话则直接获取新的access_token
        try:
            with open(os.path.join(self.basePath, self.tokenCache), 'r') as f:
                tokenInfo = json.loads(f.read())
                # 距离过期时间超过60秒则可继续使用
                if tokenInfo['expires_at'] - int(time.time()) > 60:
                    return tokenInfo['access_token']
                return self.getNewToken()
        except:
            return self.getNewToken()

    def uploadNews(self, data):
        """
        上传图文消息
        :param data: 图文列表，格式见：https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Adding_Permanent_Assets.html
        :return: {"media_id":MEDIA_ID}
        """
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        token = self.getToken()
        baseUrl = f"https://api.weixin.qq.com/cgi-bin/material/add_news?access_token={token}"
        res = checkError(self._requests('post', baseUrl, data=data))
        return res

    def uploadNewsPicture(self, mediaPath):
        """
        上传图文信息中的图片获取URL
        本接口所上传的图片不占用公众号的素材库中图片数量的100000个的限制。图片仅支持jpg/png格式，大小必须在1MB以下。
        :param mediaPath: 图片文件地址，建议使用绝对路径
        :return: 图文中可用的图片网址
        """
        token = self.getToken()
        # 如果超过1M则自动改用永久图片素材上传
        if os.path.getsize(mediaPath) >= 1024 * 1024:
            print(f"图片大小超过1M，将采用永久图片素材上传：mediaPath: {mediaPath}")
            return self.uploadMedia(mediaType='image', mediaPath=mediaPath)['url']
        mediaFile = open(mediaPath, 'rb')
        baseUrl = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
        res = checkError(self._requests('post', baseUrl, files={"media": mediaFile}))
        return res['url']

    def uploadMedia(self, mediaType, mediaPath, **kwargs):
        """
        新增其他永久素材，包括图片(image)、语音(voice)、视频(video) 和略缩图
        小视频可以上传成功，但是文件大小比较大的视频不能上传
        :param mediaPath: 素材地址，建议使用绝对路径
        :param mediaType: 素材类型
        :return: {"media_id":MEDIA_ID,"url":URL}
        """
        token = self.getToken()
        baseUrl = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type={mediaType}"
        mediaFile = open(mediaPath, 'rb')
        if mediaType == 'video':
            title = kwargs.get('title')
            introduction = kwargs.get('introduction')
            if not title or not introduction:
                raise ToodoWechatException(
                    "上传视频需要额外提供title和introduction参数，如：uploadMedia('video', '1.mp4', title='标题', introduction='简介')")
            data = {"description": json.dumps({"title": title, "introduction": introduction})}
            res = checkError(self._requests('post', baseUrl, timeout=10000, data=data, files={"media": mediaFile}))
        else:
            res = checkError(self._requests('post', baseUrl, files={"media": mediaFile}))
        return res

    def checkSignature(self, timestamp, nonce, signature):
        temp = [self.Token, timestamp, nonce]
        temp.sort()
        res = hashlib.sha1("".join(temp).encode('utf8')).hexdigest()
        return True if res == signature else False

    def replyMsg(self, msg):
        return {
            'xml': {
                'ToUserName': msg.get('FromUserName'),
                'FromUserName': msg.get('ToUserName'),
                'CreateTime': int(time.time()),
            }
        }

    def replyText(self, msg, text):
        res = self.replyMsg(msg)
        res['xml']['MsgType'] = 'text'
        res['xml']['Content'] = text
        return res

    def replyImage(self, msg, MediaId):
        res = self.replyMsg(msg)
        res['xml']['MsgType'] = 'image'
        res['xml']['Image'] = {'MediaId': MediaId}
        return res

    def replyVoice(self, msg, MediaId):
        res = self.replyMsg(msg)
        res['xml']['MsgType'] = 'voice'
        res['xml']['Voice'] = {'MediaId': MediaId}
        return res

    def replyVideo(self, msg, MediaId, title=None, desc=None):
        res = self.replyMsg(msg)
        res['xml']['MsgType'] = 'video'
        res['xml']['Video'] = {}  # {'MediaId': MediaId, 'Title': title, 'Description': desc}
        res['xml']['Video']['MediaId'] = MediaId
        if title: res['xml']['Video']['Title'] = title
        if desc: res['xml']['Video']['Description'] = desc
        return res

    def replyMusic(self, msg, pic, title=None, desc=None, url=None, hqUrl=None):
        res = self.replyMsg(msg)
        res['xml']['MsgType'] = 'music'
        res['xml']['Music'] = {'ThumbMediaId': pic}
        if title: res['xml']['Music']['Title'] = title
        if desc: res['xml']['Music']['Description'] = desc
        if url: res['xml']['Music']['MusicURL'] = url
        if hqUrl: res['xml']['Music']['HQMusicUrl'] = hqUrl
        return res

    def replyArticles(self, msg, title, desc, pic, url):
        res = self.replyMsg(msg)
        res['xml']['MsgType'] = 'news'
        res['xml']['ArticleCount'] = 1
        res['xml']['Articles'] = {'item': {'Title': title, 'Description': desc, 'PicUrl': pic, 'Url': url}}
        return res