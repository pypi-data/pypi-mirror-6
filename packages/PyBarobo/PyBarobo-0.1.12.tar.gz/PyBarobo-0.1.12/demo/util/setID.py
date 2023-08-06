#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import time
import sys

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print ("Usage: {0} <Com_Port> [New Linkbot Serial ID]".format(sys.argv[0]))
    quit()
  ctx = BaroboCtx()
  ctx.connectDongleSFP(sys.argv[1])
  linkbot = ctx.getLinkbot()
  linkbot._setSerialID(sys.argv[2])
