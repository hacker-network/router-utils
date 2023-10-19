#!/usr/bin/env python3
from gateway import get_gateway
from logging import info
from qsh_ct_login import login
from socket import AF_INET
import subprocess
from systemd import systemctl_restart
import time


def keepalive(username: str, password: str):
  gwv4 = get_gateway(AF_INET)
  if not gwv4:
    info("IPv4 gateway not found, restarting systemd-networkd")
    systemctl_restart("systemd-networkd.service")
    time.sleep(3)

  ping = subprocess.run(
    ["ping", "-c1", "-W1", "223.5.5.5"], capture_output=True)
  if ping.returncode != 0:
    info("Pinging 223.5.5.5 failed, trying to log in")
    login(username, password)


if __name__ == "__main__":
  from argparse import ArgumentParser

  parser = ArgumentParser("qsh-ct-login")
  parser.add_argument("username")
  parser.add_argument("password")
  args = parser.parse_args()

  keepalive(args.username, args.password)
