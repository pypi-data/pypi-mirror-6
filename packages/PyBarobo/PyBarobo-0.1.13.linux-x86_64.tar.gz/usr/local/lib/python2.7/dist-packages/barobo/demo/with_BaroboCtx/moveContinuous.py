#!/usr/bin/env python

import barobo
from barobo import Linkbot, Dongle
import time
import sys

if sys.version_info[0] == 3:
  raw_input = input

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print ("Usage: {0} <Com_Port> [Linkbot Serial ID]".format(sys.argv[0]))
    quit()
  if len(sys.argv) == 3:
    serialID = sys.argv[2]
  else:
    serialID = None
  dongle = Dongle()
  dongle.connectDongleTTY(sys.argv[1])
  linkbot = dongle.getLinkbot(serialID)

  linkbot.resetToZero()
  print ("Moving joints forwards for 4 seconds...")
  linkbot.setJointSpeeds(120, 120, 120)
  linkbot.moveContinuous(barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD)
  raw_input("Press enter to stop.")
  linkbot.resetToZero()
  linkbot.stop()
