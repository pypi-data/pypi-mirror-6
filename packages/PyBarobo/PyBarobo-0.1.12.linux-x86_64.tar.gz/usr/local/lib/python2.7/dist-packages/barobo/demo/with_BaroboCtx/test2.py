#!/usr/bin/env python

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
  print (linkbot)
  print (linkbot.getVersion())
  linkbot.recordAnglesBegin()
  s = raw_input('Press enter to continue...')
  linkbot.recordAnglesEnd()
  linkbot.recordAnglesPlot()
  for i in range(1,4):
    linkbot.setJointSpeed(i, 120)
  linkbot.moveToNB(360, 0, -360)
  linkbot.moveWait()
  linkbot.moveToNB(0, 0, 0)
  linkbot.moveWait()
