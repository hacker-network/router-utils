#!/usr/bin/env python3
import pyroute2
from socket import AF_INET, AF_INET6, AddressFamily


def get_gateway(family: AddressFamily):
  ipr = pyroute2.IPRoute()
  default_routes = ipr.get_default_routes(family, 254)
  if len(default_routes) == 0:
    return None
  else:
    default_route = default_routes[0]
    return next(filter(lambda x: x[0] == "RTA_GATEWAY", default_route["attrs"]))[1]


if __name__ == "__main__":
  from argparse import ArgumentParser

  parser = ArgumentParser("gateway")
  parser.add_argument("-4", "--ipv4", action="store_true")
  parser.add_argument("-6", "--ipv6", action="store_true")
  args = parser.parse_args()

  exit_code = 0
  if args.ipv4:
    if gw4 := get_gateway(AF_INET):
      print(gw4)
    else:
      exit_code += 4
  if args.ipv6:
    if gw6 := get_gateway(AF_INET6):
      print(gw6)
    else:
      exit_code += 6

  exit(exit_code)
