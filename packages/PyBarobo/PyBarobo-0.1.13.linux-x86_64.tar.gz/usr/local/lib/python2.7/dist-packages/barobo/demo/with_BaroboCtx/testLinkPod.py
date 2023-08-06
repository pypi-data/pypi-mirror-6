#!/usr/bin/env python

from barobo import Linkbot, Dongle
import barobo
import time
import sys
import math

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

  print('Getting ADC values...')
  adcs = map(linkbot.getBreakoutADCVolts, [0, 1, 2, 3, 6, 7])
  print (list(adcs))

  print('Checking digital I/O...')
  # Set all pins to input
  map( lambda pin: linkbot.setBreakoutPinMode(pin, barobo.PINMODE_INPUT), range(2,14))
  linkbot.setBreakoutPinMode(2, barobo.PINMODE_OUTPUT)
  linkbot.setBreakoutPinMode(7, barobo.PINMODE_OUTPUT)
  linkbot.setBreakoutPinMode(12, barobo.PINMODE_OUTPUT)
  linkbot.setBreakoutDigitalPin(2, 0)
  linkbot.setBreakoutDigitalPin(7, 0)
  linkbot.setBreakoutDigitalPin(12, 0)
  assert linkbot.getBreakoutDigitalPin(4) == 0
  assert linkbot.getBreakoutDigitalPin(8) == 0
  assert linkbot.getBreakoutDigitalPin(13) == 0
  linkbot.setBreakoutDigitalPin(2, 1)
  linkbot.setBreakoutDigitalPin(7, 1)
  linkbot.setBreakoutDigitalPin(12, 1)
  assert linkbot.getBreakoutDigitalPin(4) == 1
  assert linkbot.getBreakoutDigitalPin(8) == 1
  assert linkbot.getBreakoutDigitalPin(13) == 1
  # Set all pins to input
  map( lambda pin: linkbot.setBreakoutPinMode(pin, barobo.PINMODE_INPUT), range(2,14))
  linkbot.setBreakoutPinMode(4, barobo.PINMODE_OUTPUT)
  linkbot.setBreakoutPinMode(8, barobo.PINMODE_OUTPUT)
  linkbot.setBreakoutPinMode(13, barobo.PINMODE_OUTPUT)
  linkbot.setBreakoutDigitalPin(4, 0)
  linkbot.setBreakoutDigitalPin(8, 0)
  linkbot.setBreakoutDigitalPin(13, 0)
  assert linkbot.getBreakoutDigitalPin(2) == 0
  assert linkbot.getBreakoutDigitalPin(7) == 0
  assert linkbot.getBreakoutDigitalPin(12) == 0
  linkbot.setBreakoutDigitalPin(4, 1)
  linkbot.setBreakoutDigitalPin(8, 1)
  linkbot.setBreakoutDigitalPin(13, 1)
  assert linkbot.getBreakoutDigitalPin(2) == 1
  assert linkbot.getBreakoutDigitalPin(7) == 1
  assert linkbot.getBreakoutDigitalPin(12) == 1
  print('Digital I/O test passed.')

  print('Checking PWM...')
  map( lambda pin: linkbot.setBreakoutPinMode(pin, barobo.PINMODE_OUTPUT), [3, 5, 6, 9, 10, 11])
  t = 0.0
  for i in range (0, 50):
    map(lambda pin: linkbot.setBreakoutAnalogPin(pin, int(127*math.sin(t*3))+127), [3, 5, 6, 9, 10, 11])
    time.sleep(0.1)
    t += 0.1
