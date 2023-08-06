#!/usr/bin/env python

from barobo.linkbot import Linkbot
from barobo import Dongle
import time
import sys
import numpy

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
  numerrors = 0
  numtries = 500
  pingsum = 0
  pings = []
  linkbot.ping()
  for _ in range(numtries):
    try:
      sys.stdout.write('.')
      sys.stdout.flush()
      ping = linkbot.ping(4)
      pings.append(ping)
    except Exception as e:
      print(e)
      numerrors += 1
      sys.stdout.write('x')
      sys.stdout.flush()
      time.sleep(1)

  sys.stdout.write('\n')
  print("{} tries, {} errors".format(numtries, numerrors))

  print("{} errors, avg ping: {}, stddev: {}".format(numerrors, numpy.mean(pings), numpy.std(pings)))

