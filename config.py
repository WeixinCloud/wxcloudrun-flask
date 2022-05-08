import os

# 是否开启debug模式
DEBUG = True

# 读取数据库环境变量
username = os.environ.get("MYSQL_USERNAME", 'root')
password = os.environ.get("MYSQL_PASSWORD", 'root')
db_address = os.environ.get("MYSQL_ADDRESS", '127.0.0.1:3306')

# 百度翻译
trans_url = 'http://api.fanyi.baidu.com/api/trans/vip/translate?q={q}&from={trans_from}&to={trans_to}&appid={appid}&salt={salt}&sign={trans_sign}'
appid = os.environ.get("APPID")
key = os.environ.get("KEY")
default_from = 'auto'
default_to = 'zh'
default_timeout = 15

#test
test_url = 'http://127.0.0.1:8056'
