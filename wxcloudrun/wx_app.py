import re
import json
from datetime import datetime

import requests
from pydantic import BaseModel

from config import settings

from .cache import Cache

WXAPP = settings.WXAPP
USERS = settings.USERS
ALLOW_JOBS = settings.ALLOW_JOBS


class WxAppSender():

    def send(self, body, *args, **kwargs):

        if isinstance(body, str):
            output = self.converter_chatwoot(body, *args, **kwargs)
        else:
            output = {}
        self.__send__(output)


    @classmethod
    def converter_chatwoot(cls, message, *args, **kwargs):
        tousers = [
            USERS.get("admin", {}).get("wxid", ""),
        ]
        if kwargs.get('site', '') == 'oversea':
            tousers.append(USERS.get("LingLong", {}).get("wxid", ""))
        else:
            tousers.append(USERS.get("GYuMan", {}).get("wxid", ""))
        print("converter_chatwoot")
        return {
            "touser": "|".join(tousers),
            "msgtype": "markdown",
            "agentid": WXAPP['agentid'],
            "markdown": {
                "content": message
            },
            "safe": 0,
            "enable_id_trans": 0,
            "enable_duplicate_check": 0
        }

    @classmethod
    def line_output(cls, label, text, color=""):
        if text == "":
            return ""
        if label != "":
            label = label + "："
        if color != "":
            text = f"""<font color=\"{color}\">{text}</font>"""
        return "> " + label + text + "\n"

    @staticmethod
    def description_output(assignees, description):
        prefix = "".join(["@" + USERS.get(assignee.username, {}).get("name", "") + " " for assignee in assignees])
        regexp = r'@(.*?)( |$)'

        def replace(match):
            item = match.groups()[0]
            if item in [assignee.username for assignee in assignees]:
                return ""
            name = USERS.get(item, {}).get("name")
            return f"@{name} " if name else f"@{item} "

        return prefix + re.sub(regexp, replace, description)

    @classmethod
    def __send__(cls, content):

        url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=2ba90711-bbca-4080-a6ce-620f9a3c3175"  # 这里就是群机器人的Webhook地址
        headers = {"Content-Type": "application/json"}  # http数据头，类型为json
        data = {
            "msgtype": "text",
            "text": {
                "content": content,  # 让群机器人发送的消息内容。
                "mentioned_list": [],
            }
        }
        r = requests.post(url, headers=headers, json=data)  # 利用requests库发送post请求




sender_instance = WxAppSender()
