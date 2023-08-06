#!/usr/bin/env python

from barobo import Linkbot
import time

if __name__ == "__main__":
  linkbot = Linkbot()

  linkbot.connect()
  #linkbot.setAcceleration(120)
  linkbot.resetToZero()
  linkbot.moveTo(180, 180, 180)
  linkbot.moveTo(0, 0, 0)

  linkbot.disconnect()
  time.sleep(1)

  linkbot.connect()
  #linkbot.setAcceleration(120)
  linkbot.resetToZero()
  linkbot.moveTo(180, 180, 180)
  linkbot.moveTo(0, 0, 0)

