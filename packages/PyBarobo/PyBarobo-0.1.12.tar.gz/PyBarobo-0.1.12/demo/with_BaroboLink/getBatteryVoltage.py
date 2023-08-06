#!/usr/bin/env python

from barobo import Linkbot
import time

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()

  for _ in range(5):
    print (linkbot.getBatteryVoltage())
    time.sleep(0.5)
