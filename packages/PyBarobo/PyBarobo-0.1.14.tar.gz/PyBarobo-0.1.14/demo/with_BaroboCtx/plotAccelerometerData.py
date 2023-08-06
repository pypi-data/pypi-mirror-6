#!/usr/bin/env python

from barobo import Linkbot, Dongle
import pylab
import threading
import time
import math
import sys

if sys.version_info[0] == 3:
  raw_input = input

class RecordAccelData(threading.Thread):
  def __init__(self, linkbot):
    threading.Thread.__init__(self)
    self.continueRunning = False
    self.linkbot = linkbot
    self.times = []
    self.mags = []

  def run(self):
    while self.continueRunning:
      self.times.append(time.time() - self.startTime)
      alpha = self.linkbot.getAccelerometerData()
      mymag = 0
      for a in alpha:
        mymag += a**2
      mymag = math.sqrt(mymag)
      self.mags.append(mymag)
      time.sleep(0.01)

  def start(self):
    self.continueRunning = True
    self.startTime = time.time()
    threading.Thread.start(self)

  def join(self, *args, **kwargs):
    self.continueRunning = False
    threading.Thread.join(self, *args, **kwargs)

  def plot(self):
    pylab.plot(self.times, self.mags)
    pylab.show()

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

  record = RecordAccelData(linkbot)
  record.start()
  raw_input('Press enter to stop recording')
  record.join()
  record.plot()

