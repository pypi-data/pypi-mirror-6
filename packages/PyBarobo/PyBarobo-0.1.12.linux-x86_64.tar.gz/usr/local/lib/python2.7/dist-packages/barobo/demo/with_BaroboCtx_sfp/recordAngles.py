#!/usr/bin/env python

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
  linkbot.resetToZero()
  linkbot.recordAnglesBegin(delay=0.1)
  linkbot.smoothMoveTo(1, 100, 100, 100, 360)
  linkbot.smoothMoveTo(2, 100, 100, 100, 360)
  linkbot.smoothMoveTo(3, 100, 100, 100, 360)
  linkbot.moveWait()
  linkbot.recordAnglesEnd()
  linkbot.recordAnglesPlot()
