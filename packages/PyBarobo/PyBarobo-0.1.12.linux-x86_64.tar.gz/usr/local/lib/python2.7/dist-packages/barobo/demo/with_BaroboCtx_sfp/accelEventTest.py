#!/usr/bin/env python

from barobo import Linkbot, Dongle
import sys
import time

def jointcb(millis, j1, j2, j3):
  print('joint: {} {} {} {}'.format(millis, j1, j2, j3))

def accelcb(millis, j1, j2, j3):
  print('accel: {} {} {} {}'.format(millis, j1, j2, j3))

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

  linkbot.enableAccelEventCallback(accelcb)
  time.sleep(3)
  raise Exception('boop.')
