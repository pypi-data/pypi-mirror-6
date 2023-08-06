#!/usr/bin/env python

from barobo.linkbot import Linkbot
import time
import sys

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print('Usage: {0} <Bluetooth MAC Address>'.format(sys.argv[0]))
    sys.exit(0)
  linkbot = Linkbot()
  linkbot.connectMobotBluetooth(sys.argv[1])

  linkbot.resetToZero()
  linkbot.setAcceleration(0);
  linkbot.setJointSpeeds(90, 90, 90)
  time.sleep(3)
  for _ in range(10):
    linkbot.moveTo(-360, 360, 360)
    linkbot.moveTo(0, 0, 0)
