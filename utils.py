import os.path
import yaml

BASE_DIR = os.path.dirname('./')
CONFIG = 'config.yaml'
CONFIG_PATH = os.path.join(BASE_DIR, CONFIG)


def load_conf():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        conf = yaml.safe_load(f.read())
        return conf


if __name__ == '__main__':
    print(load_conf())
