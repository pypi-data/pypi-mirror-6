#!/usr/bin/env python

from barobo import Linkbot

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()

  linkbot.resetToZero()
  print ("Moving all joints 90 degrees...")
  linkbot.move(90, 90, 90)
