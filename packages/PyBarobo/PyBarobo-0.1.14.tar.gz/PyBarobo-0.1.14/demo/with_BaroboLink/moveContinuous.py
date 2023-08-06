#!/usr/bin/env python

import barobo
from barobo import Linkbot

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()

  linkbot.resetToZero()
  print ("Moving joints forwards...")
  linkbot.setJointSpeeds(120, 120, 120)
  linkbot.moveContinuous(barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD, barobo.ROBOT_FORWARD)
  raw_input("Press enter to stop.")
  linkbot.stop()
