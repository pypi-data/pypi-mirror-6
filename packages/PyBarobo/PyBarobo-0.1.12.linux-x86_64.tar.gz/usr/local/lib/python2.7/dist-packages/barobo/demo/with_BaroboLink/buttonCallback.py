#!/usr/bin/env python

from barobo import Linkbot

def callback(mask, buttons, userdata):
  print ("Button press! mask: {} buttons: {}".format(hex(mask), hex(buttons)))

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()
  linkbot.enableButtonCallback(callback)
  raw_input('Button callbacks have been enabled. Press buttons on the Linkbot. Hit Enter when done')

