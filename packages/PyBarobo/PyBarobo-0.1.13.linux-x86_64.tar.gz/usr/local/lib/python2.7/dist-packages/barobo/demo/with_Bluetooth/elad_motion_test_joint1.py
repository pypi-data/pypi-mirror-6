#!/usr/bin/env python

from barobo.linkbot import Linkbot
from barobo import BaroboCtx
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

  ctx = BaroboCtx()
  ctx.connectDongleTTY(sys.argv[1])
  linkbot = ctx.getLinkbot(serialID)

#linkbot.resetToZero()
  linkbot.setAcceleration(0);
  linkbot.setJointSpeeds(90, 90, 90)
  time.sleep(3)
  for _ in range(10):
    linkbot.moveJointTo(1, -360)
    linkbot.moveJointTo(1, 0)
