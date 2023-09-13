# 创建应用实例
import sys

from wxcloudrun import app

# 启动Flask Web服务
if __name__ == '__main__':
    print(sys.argv)
    app.run(host=sys.argv[1], port=sys.argv[2])

# from gevent import pywsgi
#
# if __name__ == '__main__':
#     server = pywsgi.WSGIServer(('0.0.0.0', 8399), app)
#     server.serve_forever()