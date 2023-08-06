#!/usr/bin/env python

from barobo.linkbot import Linkbot
import time

if __name__ == "__main__":
  linkbot = Linkbot()
#linkbot.connectBluetooth('00:06:66:4D:F6:6F')
  linkbot.connectBluetooth('00:06:66:45:D9:F5')

  linkbot.setMotorPowers(255, 150, 255)
