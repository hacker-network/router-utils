#!/usr/bin/env python3
from pyroute2 import IPRoute
from gateway import get_gateway
from logging import error, info, warning
import os
from qsh_ct_login import login
from selenium.common.exceptions import TimeoutException
from socket import AF_INET
import subprocess
from systemd import systemctl_restart
import time


def check_online() -> bool:
  ping = subprocess.run(
    ["ping", "-c1", "-W1", "223.5.5.5"], capture_output=True)
  return ping.returncode == 0


def link_state(ifname):
  with IPRoute() as ipr:
    if not (id := ipr.link_lookup(ifname=ifname)) or len(id) == 0:
      return None
    link = ipr.get_links(id[0])[0]
    return next(filter(lambda x: x[0] == "IFLA_OPERSTATE", link["attrs"]))[1]


def keepalive(ifname: str, username: str, password: str) -> int:
  # Check link state
  if not (state := link_state(ifname)):
    error(f"Uplink interface {ifname} not found.")
    return 1
  elif state != "UP":
    error(f"Uplink interface {ifname} not up. Giving up.")
    return 1

  # Check IPv4 gateway
  gw_not_found = False
  for i in range(3):
    gwv4 = get_gateway(AF_INET)
    if gwv4:
      break
    else:
      gw_not_found = True
      warning("IPv4 gateway not found, "
              f"restarting systemd-networkd... ({i + 1})")
      systemctl_restart("systemd-networkd.service")
      time.sleep(3)
  else:
    error("Receiving IPv4 gateway failed 3 times. Giving up.")
    return 1

  # Check online and login
  if check_online():
    if gw_not_found:
      info("Seems network is online.")
    return 0
  else:
    warning("Network not online, trying to log in...")
    try:
      login(username, password)
    except TimeoutException:
      error("Login timed out, is login gateway's IP changed?")
      return 1
    except Exception as e:
      error(f"Login failed: {e}")
      return 1

  # Check online again
  if check_online():
    info("Network is online after login.")
    return 0
  else:
    error("Network still fails after login. "
          "Restarting systemd-networkd and try next time.")
    systemctl_restart("systemd-networkd.service")
    return 1


if __name__ == "__main__":
  from argparse import ArgumentParser
  from logger import init_logger

  parser = ArgumentParser("qsh-ct-keepalive")
  parser.add_argument("ifname", help="Uplink interface name")
  parser.add_argument("username", help="Login username")
  parser.add_argument("password", help="Login password")
  parser.add_argument("-e", "--stderr",
                      help="Logs to stderr instead of file when run as root",
                      action="store_true")
  args = parser.parse_args()

  if os.geteuid() == 0 and not args.stderr:
    init_logger("/var/log/qsh-ct-keepalive.log")
  else:
    init_logger("/dev/stderr")

  exit(keepalive(args.ifname, args.username, args.password))
