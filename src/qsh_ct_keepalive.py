#!/usr/bin/env python3
import os
from gateway import get_gateway
from logging import error, info, warning
from logging.handlers import RotatingFileHandler
from qsh_ct_login import login
from selenium.common.exceptions import TimeoutException
from socket import AF_INET
import subprocess
from systemd import systemctl_restart
import time


def keepalive(username: str, password: str) -> int:
  for i in range(3):
    gwv4 = get_gateway(AF_INET)
    if gwv4:
      break
    else:
      warning(f"IPv4 gateway not found, restarting systemd-networkd ({i + 1})")
      systemctl_restart("systemd-networkd.service")
      time.sleep(3)
  else:
    error("failed to receive IPv4 gateway in 3 times. Giving up.")
    return 1

  ping = subprocess.run(
    ["ping", "-c1", "-W1", "223.5.5.5"], capture_output=True)
  if ping.returncode == 0:
    info("Seems network is online.")
    return 0
  else:
    warning("Pinging 223.5.5.5 failed, trying to log in")
    try:
      login(username, password)
    except TimeoutException:
      error("Login timed out, is login gateway's IP changed?")
      return 1
    except Exception as e:
      error(f"Login failed: {e}")
      return 1


if __name__ == "__main__":
  from argparse import ArgumentParser
  from logger import setup_root_logger

  parser = ArgumentParser("qsh-ct-keepalive")
  parser.add_argument("username")
  parser.add_argument("password")
  parser.add_argument("-e", "--stderr", action="store_true")
  args = parser.parse_args()

  if os.geteuid() == 0 and not args.stderr:
    setup_root_logger("/var/log/qsh-ct-keepalive.log")
  else:
    setup_root_logger("/dev/stderr")

  exit(keepalive(args.username, args.password))
