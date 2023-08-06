#!/usr/bin/env python

from barobo import Linkbot

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()

  for i in range(1,4):
    print ("Joint {} angle: {}".format(i, linkbot.getJointAngle(i)))
