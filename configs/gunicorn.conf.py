import os
import sys

sys.path.append('./modules/')
sys.path.append(os.environ['AIL_BIN'])

from lib.ConfigLoader import ConfigLoader


config_loader = ConfigLoader()

try:
    host = config_loader.get_config_str("Flask", "host")
except Exception:
    host = '0.0.0.0'

try:
    port = config_loader.get_config_int("Flask", "port")
except Exception:
    port = 7000

bind = f"{host}:{port}"
workers = 2
worker_class = 'sync'
timeout = 180
loglevel = 'info'
limit_request_line = 0