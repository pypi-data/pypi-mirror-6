#!/usr/bin/env python

from barobo.linkbot import Linkbot
import time
import sys

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print('Usage: {0} <Bluetooth MAC Address>'.format(sys.argv[0]))
    sys.exit(0)
  linkbot = Linkbot()
  linkbot.connectBluetooth(sys.argv[1])

  linkbot.resetToZero()
  print ("Moving joints to 90 degrees...")
  linkbot.driveTo(90, 90, 90)
  time.sleep(1)
  print ("Moving joints to 0 degrees...")
  linkbot.driveTo(0, 0, 0)
