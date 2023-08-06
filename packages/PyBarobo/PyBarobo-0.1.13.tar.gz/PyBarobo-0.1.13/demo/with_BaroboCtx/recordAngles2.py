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
  dongle.connectDongleTTY(sys.argv[1])
  linkbot = dongle.getLinkbot(serialID)
  linkbot.stop()
  linkbot.recordAnglesBegin(delay=0.1)
  raw_input('Press enter to stop recording')
  linkbot.recordAnglesEnd()
  linkbot.recordAnglesPlot()
