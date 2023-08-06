#!/usr/bin/env python

from barobo import Linkbot, Dongle
import barobo
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

  linkbot.setBuzzerFrequency(440);
  time.sleep(1)
  linkbot.setBuzzerFrequency(880);
  time.sleep(1)
  linkbot.setBuzzerFrequency(440);
  time.sleep(1)
  linkbot.setBuzzerFrequency(0);
