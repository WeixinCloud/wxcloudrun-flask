import os

# 是否开启debug模式
DEBUG = True

# 读取数据库环境变量
username = os.environ.get("MYSQL_USERNAME", 'root')
password = os.environ.get("MYSQL_PASSWORD", 'root')
db_address = os.environ.get("MYSQL_ADDRESS", '127.0.0.1:3306')
os.environ['env'] ='prod'
tools_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wxcloudrun','cache')
print(tools_path)

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="CEEG",
    environments=True,
    env_switcher="ENV",
    settings_files=['settings.yaml','common.yaml'],
    root_path=os.path.dirname(os.path.abspath(__file__))
)
