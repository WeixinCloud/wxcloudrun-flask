import logging
from datetime import datetime

import requests
import xmltodict
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
from wxcloudrun.tools import WechatMP
from wxcloudrun.wx_app import WxAppSender


@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')


@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)


token = "asdfdasfafd"
appId = "wxce3c081851aedbac"
wmp = WechatMP(Token=token, appId=appId, secret='')
sender = WxAppSender()
logger = logging.getLogger('log')

@app.route('/test', methods=['POST'])
def test2():
    data: bytes = request.data
    logger.error("--------data----",str(data))
    print("-------------data--------")

    try:
        print(data)
        logger.info(data)
        logger.info(data.decode())
    except Exception as e:
        logger.error(e)
    msg = xmltodict.parse(data.decode()).get('xml')
    msgType = msg.get('MsgType')
    sender.send(msg)
    if msg.get('action', '') == 'CheckContainerPath':
        return make_succ_empty_response()
    print(msg)


    # send_data =  {
    #        "touser":"OPENID",
    #        "template_id":"ngqIpbwh8bUfcSsECmogfXcV14J0tQlEpBO27izEYtY",
    #        "url":"http://www.baidu.com",
    #        "miniprogram":{
    #        },
    #        "client_msg_id":"MSG_000001",
    #        "data":{
    #
    #                "keyword1":{
    #                    "value":"巧克力"
    #                },
    #                "keyword2": {
    #                    "value":"39.8元"
    #                },
    #                "keyword3": {
    #                    "value":"2014年9月22日"
    #                }
    #        }
    #    }

    res = wmp.replyText(msg, '您好，欢迎您关注并联系中电变压器，您可点击链接随时与我们取得联系：https://work.weixin.qq.com/kfid/kfc810b2cf6bdf83836')
    # res = wmp.replyText(msg, str(data))

    return xmltodict.unparse(res)

@app.route('/getMessage', methods=['POST'])
def getMessage():
    data: bytes = request.data
    msg = xmltodict.parse(data.decode()).get('xml')
    tousername = msg.get('ToUserName')
    fromusername = msg.get('FromUserName')

    url = f"http://api.weixin.qq.com/cgi-bin/message/template/send"
    send_data =  {
           "touser":tousername,
           "template_id":"gzwCdG32PHvIoAwKzFkzqi8PfRhCYMNcxfFtkqnfHmA",
           "url":"http://www.baidu.com",
           "miniprogram":{
           },
           "client_msg_id":"MSG_000001",
           "data":{

                   "character_string2.DATA":{
                       "value":"111"
                   },
                   "thing3.DATA": {
                       "value":"222"
                   },
                   "time6.DATA": {
                       "value":"222"
                   },
                   "thing9.DATA": {
                       "value":"333"
                   },
                   "thing4.DATA": {
                       "value":"4444"
                   }
           }
       }
    resp = requests.post(url, json=send_data)
    # url = f"http://api.weixin.qq.com/cgi-bin/user/info?openid={msg}&lang=zh_CN"
    # url = f"http://api.weixin.qq.com/sns/userinfo?openid={msg}&lang=zh_CN"
    print(resp.json())
    return make_succ_response(resp.json())
