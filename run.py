# 创建应用实例
import sys
import logging

from wxcloudrun import app

logging.basicConfig(level=logging.INFO)

# 启动Flask Web服务
if __name__ == '__main__':
    app.run(host=sys.argv[1], port=sys.argv[2])
