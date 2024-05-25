from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import time
import xmltodict
import logging

logger = logging.getLogger(__name__)


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



@app.route('/api/wx', methods=['GET', 'POST'])
def wx_check():
    import hashlib
    from config import wx_token

    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    echostr = request.args.get('echostr')

    token = wx_token

    list = [token, timestamp, nonce]
    list.sort()
    sha1 = hashlib.sha1()
    map(sha1.update, list)
    hashcode = sha1.hexdigest()
    print("handle/GET func: hashcode, signature: ", hashcode, signature)
    if hashcode == signature:
        return echostr
    else:
        return ""


@app.route('/api/wx/test', methods=['GET', 'POST'])
def wx_test():
    body = request.get_json()
    logger.info("body: {}", body)
    return ""

@app.route('/api/wx/msg', methods=['GET', 'POST'])
def handler_msg():
    body = request.get_data()
    req = xmltodict.parse(body)['xml']
    print(req)
    content = req['Content']
    to_user = req['ToUserName']
    from_user = req['FromUserName']

    tpl = '''
    <xml>
        <ToUserName><![CDATA[{toUser}]]></ToUserName>
        <FromUserName><![CDATA[{fromUser}]]></FromUserName>
        <CreateTime>{createTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
    </xml>
    '''
    msg = tpl.format(toUser=from_user, fromUser=to_user,
                     createTime=int(time.time()), content=content)
    return msg

