#!/usr/bin/env python

from barobo import Linkbot, Dongle
import time
import sys
import math

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

  for i in range(0, 1000, 1):
    linkbot.setBuzzerFrequency(int((math.sin(i/100)+1)*1000))

  linkbot.stop()

