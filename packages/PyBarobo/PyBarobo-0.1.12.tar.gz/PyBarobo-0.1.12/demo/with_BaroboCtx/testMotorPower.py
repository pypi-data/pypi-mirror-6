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

  linkbot.resetToZero()
  linkbot.stop()
  linkbot.setMotorPowers(0, 255, 255)
  time.sleep(1)
  startAngles = linkbot.getJointAngles()
  time.sleep(5)
  endAngles = linkbot.getJointAngles()
  linkbot.stop()
  for start, end in zip(startAngles, endAngles):
    print ('Forward Speed: {}'.format((end-start)/5.0))
  linkbot.setMotorPowers(0, -255, -255)
  time.sleep(1)
  startAngles = linkbot.getJointAngles()
  time.sleep(5)
  endAngles = linkbot.getJointAngles()
  linkbot.stop()
  for start, end in zip(startAngles, endAngles):
    print ('Backward Speed: {}'.format((end-start)/5.0))
