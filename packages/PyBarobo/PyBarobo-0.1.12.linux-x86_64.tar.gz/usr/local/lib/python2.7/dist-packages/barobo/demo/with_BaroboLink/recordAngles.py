#!/usr/bin/env python

from barobo import Linkbot

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()
  linkbot.resetToZero()
  linkbot.recordAnglesBegin(delay=0.1)
  linkbot.smoothMoveTo(1, 100, 100, 120, 360)
  linkbot.smoothMoveTo(2, 100, 100, 120, 360)
  linkbot.smoothMoveTo(3, 100, 100, 120, 360)
  linkbot.moveWait()
  linkbot.recordAnglesEnd()
  linkbot.recordAnglesPlot()
