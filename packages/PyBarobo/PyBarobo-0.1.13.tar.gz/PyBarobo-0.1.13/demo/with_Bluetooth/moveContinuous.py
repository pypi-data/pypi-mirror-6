#!/usr/bin/env python

import barobo
from barobo import Linkbot, BaroboCtx
import time
import sys

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print('Usage: {0} <Bluetooth MAC Address>'.format(sys.argv[0]))
    sys.exit(0)
  linkbot = Linkbot()
  linkbot.connectMobotBluetooth(sys.argv[1])

  linkbot.resetToZero()
  print ("Moving joints forwards...")
  linkbot.setJointSpeeds(-120, 120, 120)
  linkbot.moveContinuous(barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD)
  raw_input("Press enter to stop.")
  linkbot.moveContinuous(barobo.ROBOT_BACKWARD, barobo.ROBOT_BACKWARD, barobo.ROBOT_BACKWARD)
  raw_input("Press enter to stop.")
  linkbot.resetToZero()
  linkbot.stop()
