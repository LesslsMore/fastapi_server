from dotenv import load_dotenv, find_dotenv

from plugin.db.postgres import init_postgres

# config = load_config()
# load_dotenv('../config/.env.win')
# load_dotenv('config/.env.win')
# load_dotenv('config/.env.render')
# load_dotenv('config/.env.vercel')

# pg_engine = init_postgres()
#
#
# # 获取数据库会话的依赖
# def get_session():
#     return Session(pg_engine)

env_file = '.env.dev'
# 运行环境不为空时按命令行参数加载对应.env文件

# 加载配置
load_dotenv(find_dotenv(env_file))

# redis_client = init_redis_conn()
