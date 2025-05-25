import os
import yaml
import dotenv

def load_config():
    """
    读取同目录下的 config.yml 文件并返回配置内容。
    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def load_dotenv(dotenv_path=None):
    """
    加载 .env 文件中的环境变量。
    :param dotenv_path: .env 文件路径，默认为当前目录下的 .env
    """
    if dotenv_path is None:
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    dotenv.load_dotenv(dotenv_path)

config = load_config()
load_dotenv('config/.env.win')