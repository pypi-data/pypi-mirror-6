#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import time

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connectBluetooth('00:06:66:4D:F6:6F')
  linkbot.resetToZero()
  linkbot.recordAnglesBegin(delay=0.1)
  linkbot.smoothMoveTo(1, 100, 100, 100, 360)
  linkbot.smoothMoveTo(2, 100, 100, 100, 360)
  linkbot.smoothMoveTo(3, 100, 100, 100, 360)
  linkbot.moveWait()
  linkbot.recordAnglesEnd()
  linkbot.recordAnglesPlot()
