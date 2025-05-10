import os
import yaml

def load_config():
    """
    读取同目录下的 config.yml 文件并返回配置内容。
    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

config = load_config()