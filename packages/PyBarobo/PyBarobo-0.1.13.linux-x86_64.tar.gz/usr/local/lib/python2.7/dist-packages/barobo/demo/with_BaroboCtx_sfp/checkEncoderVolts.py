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

  linkbot.setJointSpeeds(45, 45, 45)
  linkbot.moveContinuous(barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD)
  #linkbot.moveContinuous(barobo.ROBOT_BACKWARD, barobo.ROBOT_BACKWARD, barobo.ROBOT_BACKWARD)
  while True:
    results = map(linkbot._getADCVolts, range(8))
    print(results)
    print([1, (results[5] - results[6])*2, results[5], results[6]])
    print([2, (results[1] - results[2])*2, results[1], results[2]])
    time.sleep(0.2)
