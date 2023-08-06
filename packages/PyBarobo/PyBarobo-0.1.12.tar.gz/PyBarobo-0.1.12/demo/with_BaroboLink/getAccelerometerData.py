#!/usr/bin/env python

from barobo import Linkbot
import time

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()

  for _ in range(20):
    print (linkbot.getAccelerometerData())
    time.sleep(0.5)
