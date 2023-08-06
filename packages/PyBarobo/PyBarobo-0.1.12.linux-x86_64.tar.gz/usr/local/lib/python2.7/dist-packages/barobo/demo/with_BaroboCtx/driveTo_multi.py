#!/usr/bin/env python

from barobo import Linkbot, Dongle
import time

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot2 = Linkbot()
  linkbot.connect()
  linkbot2.connect()

  linkbot.resetToZero()
  linkbot2.resetToZero()
  print ("Moving joints to 90 degrees...")
  linkbot.driveToNB(90, 90, 90)
  linkbot2.driveToNB(90, 90, 90)
  time.sleep(1)
  print ("Moving joints to 0 degrees...")
  linkbot.driveToNB(0, 0, 0)
  linkbot2.driveToNB(0, 0, 0)
