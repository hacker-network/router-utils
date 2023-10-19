import logging
from logging.handlers import RotatingFileHandler
from logging import Formatter


def setup_root_logger(path: str):
  logging.root.level = logging.INFO
  handler = RotatingFileHandler(path, maxBytes=100 << 20, backupCount=1)
  handler.setFormatter(Formatter("%(asctime)s %(levelname)s %(message)s"))
  logging.root.addHandler(handler)
