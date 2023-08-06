#!/usr/bin/env python

from barobo import Linkbot
import time
import sys

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()

  linkbot.resetToZero()
  linkbot.stop()
  linkbot.setMotorPowers(-255, -255, -255)
