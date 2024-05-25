# coding:utf-8
import requests as rq

body = {
    "signature": "ilovetracholar",
    "timestamp": 1716626952,
    "nonce": "rwerwer",
    "echostr": "test"
}

rsp = rq.get('http://127.0.0.1/api/wx', content=body)
print(rsp.content)