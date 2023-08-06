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
  print ("Moving joints to 90 degrees...")
  linkbot.driveTo(90, 90, 90)
  time.sleep(1)
  print ("Moving joints to 0 degrees...")
  linkbot.driveTo(0, 0, 0)
