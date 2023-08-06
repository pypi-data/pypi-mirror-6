#!/usr/bin/env python

# Note: This demo will only work if you have a Barobo breakout-board currently
# attached to the linkbot.

from barobo import Linkbot

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()

  adcs = map(linkbot.getBreakoutADC, range(0,8))
  print(map(lambda x: x/1024.0*5.0, adcs))
