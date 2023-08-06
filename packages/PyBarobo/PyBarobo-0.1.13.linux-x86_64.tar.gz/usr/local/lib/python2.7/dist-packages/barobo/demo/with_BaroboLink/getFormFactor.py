#!/usr/bin/env python

from barobo import Linkbot

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()

  print (linkbot.getFormFactor())
