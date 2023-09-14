import re


import requests


from config import settings


WXAPP = settings.WXAPP
USERS = settings.USERS
ALLOW_JOBS = settings.ALLOW_JOBS


class WxAppSender():

    def send(self, body, *args, **kwargs):

        self.__send__(body)


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
                "content": f"中电变压器微信公众号有一条新的私信：{content.get('Content')},发送方{content.get('FromUserName','')},接收方{content.get('ToUserName','')}",  # 让群机器人发送的消息内容。
                "mentioned_list": [],
            }
        }
        r = requests.post(url, headers=headers, json=data)  # 利用requests库发送post请求


# <xml>
#   <ToUserName><![CDATA[toUser]]></ToUserName>
#   <FromUserName><![CDATA[fromUser]]></FromUserName>
#   <CreateTime>1348831860</CreateTime>
#   <MsgType><![CDATA[text]]></MsgType>
#   <Content><![CDATA[this is a test]]></Content>
#   <MsgId>1234567890123456</MsgId>
#   <MsgDataId>xxxx</MsgDataId>
#   <Idx>xxxx</Idx>
# </xml>


sender_instance = WxAppSender()
