import random
import hashlib
import requests
from datetime import datetime
from flask import render_template, request
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response
import config


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


@app.route('/api/fanyi', methods=['POST'])
def fanyi():
    """
    :return: 百度翻译response
    """
    params = request.get_json()
    if 'fanyi_content' not in params:
        return make_err_response('缺少fanyi_content参数')
    q = params['fanyi_content']
    salt = random.randint(100, 999)
    trans_from = config.default_from
    trans_to = config.default_to
    appid = config.appid
    trans_key = config.key
    tmp = str(appid) + q + str(salt) + trans_key
    trans_sign = hashlib.md5(tmp.encode(encoding='utf-8')).hexdigest()
    trans_url = config.trans_url.format(q=q, trans_from=trans_from, trans_to=trans_to,
                                         appid=appid, salt=salt, trans_sign=trans_sign)
    res = requests.get(trans_url, timeout=config.default_timeout)
    trans_result = res.json().get("trans_result", "")
    if trans_result:
        trans_result = trans_result[0].get("dst", "")
    return make_succ_response(trans_result)
