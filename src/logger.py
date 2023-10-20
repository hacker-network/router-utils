from logging.handlers import RotatingFileHandler
from logging import Formatter, root as root_logger, INFO


def init_logger(path: str):
  root_logger.level = INFO
  handler = RotatingFileHandler(path, maxBytes=100 << 20, backupCount=1)
  handler.setFormatter(Formatter("%(asctime)s %(levelname)s %(message)s"))
  root_logger.addHandler(handler)
