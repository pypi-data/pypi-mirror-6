#!/usr/bin/env python

from barobo import Linkbot

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()
  print (linkbot)
  print (linkbot.getVersion())
  linkbot.recordAnglesBegin()
  s = raw_input('Press enter to continue...')
  linkbot.recordAnglesEnd()
  linkbot.recordAnglesPlot()
  for i in range(1,4):
    linkbot.setJointSpeed(i, 120)
  while True:
    linkbot.moveToNB(360, 0, -360)
    linkbot.moveWait()
    linkbot.moveToNB(0, 0, 0)
    linkbot.moveWait()
