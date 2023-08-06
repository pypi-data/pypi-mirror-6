#!/usr/bin/env python

from barobo import Linkbot
import time

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()

  linkbot.resetToZero()
  print ("Moving joints to 90 degrees...")
  linkbot.driveTo(90, 90, 90)
  time.sleep(1)
  print ("Moving joints to 0 degrees...")
  linkbot.driveTo(0, 0, 0)
