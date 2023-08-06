#!/usr/bin/env python

import barobo
from barobo import Linkbot, Dongle
import time
import sys

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print ("Usage: {0} <Com_Port> [Linkbot Serial ID]".format(sys.argv[0]))
    quit()
  if len(sys.argv) == 3:
    serialID = sys.argv[2]
  else:
    serialID = None
  dongle = Dongle()
  dongle.connectDongleSFP(sys.argv[1])
  linkbot = dongle.getLinkbot(serialID)

  linkbot.setMotorPowers(255, 255, 255)
  while True:
    results = linkbot.getJointAnglesTime()
    print(results)
    time.sleep(0.2)
