#!/usr/bin/env python3
from logger import setup_root_logger
from logging import error
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from time import sleep

# This may subject to change over time
login_gw = "http://172.25.249.64"


def login(username: str, password: str, headless: bool = True):
  options = ChromeOptions()
  options.add_argument("--no-sandbox")
  if headless:
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")

  driver = Chrome(options=options, service=ChromeService("/usr/bin/chromedriver"))
  driver.set_page_load_timeout(10)
  driver.set_script_timeout(10)

  driver.get(login_gw)
  sleep(1)

  # element not interactable using find_element and send_keys
  set_username = f'document.getElementById("username").value="{username}"'
  set_password = f'document.getElementById("pwd").value="{password}"'
  driver.execute_script(set_username)
  driver.execute_script(set_password)

  driver.find_element(By.ID, "SLoginBtn_1").click()
  sleep(1)


if __name__ == "__main__":
  from argparse import ArgumentParser

  parser = ArgumentParser("qsh-ct-login")
  parser.add_argument("username")
  parser.add_argument("password")
  args = parser.parse_args()

  setup_root_logger("/dev/stderr")

  try:
    login(args.username, args.password)
  except Exception as e:
    error(f"Login failed: {e}")
    exit(1)
