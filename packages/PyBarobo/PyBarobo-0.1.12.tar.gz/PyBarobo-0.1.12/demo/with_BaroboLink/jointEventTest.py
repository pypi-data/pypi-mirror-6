#!/usr/bin/env python

from barobo import Linkbot, BaroboCtx
import sys

if sys.version_info[0] == 3:
  raw_input = input

def jointcb(millis, j1, j2, j3):
  print('joint: {} {} {} {}'.format(millis, j1, j2, j3))

def accelcb(millis, j1, j2, j3):
  print('accel: {} {} {} {}'.format(millis, j1, j2, j3))

if __name__ == "__main__":
  linkbot = Linkbot()
  linkbot.connect()

  instr = 'c'
  jointThresh = 1
  accelThresh = 0.1
  jointCBEnabled = False
  accelCBEnabled = False
  while instr != 'q':
    instr = raw_input(
        'Commands:\n'
        '1 : Enable/Disable joint callback\n'
        '2 : Enable/Disable accel callback\n'
        '3 : Increase joint threshold\n'
        '4 : Decrease joint threshold\n'
        '5 : Increase accel threshold\n'
        '6 : Decrease accel threshold\n'
        'q : quit' )
    if instr == '1':
      if jointCBEnabled:
        linkbot.disableJointEventCallback()
        jointCBEnabled = False
        print('Joint callback disabled.')
      else:
        linkbot.enableJointEventCallback(jointcb)
        jointCBEnabled = True 
        print('Joint callback enabled.')
    elif instr == '2':
      if accelCBEnabled:
        linkbot.disableAccelEventCallback()
        accelCBEnabled = False
        print('Accel callback disabled.')
      else:
        linkbot.enableAccelEventCallback(accelcb)
        accelCBEnabled = True 
        print('Accel callback enabled.')
    elif instr == '3':
      jointThresh += 1
      linkbot.setJointEventThreshold(jointThresh)
      print('Joint threshold set to {}'.format(jointThresh))
    elif instr == '4':
      jointThresh -= 1
      linkbot.setJointEventThreshold(jointThresh)
      print('Joint threshold set to {}'.format(jointThresh))
    elif instr == '5':
      accelThresh += 0.1
      linkbot.setAccelEventThreshold(accelThresh)
      print('Accel threshold set to {}'.format(accelThresh))
    elif instr == '6':
      accelThresh -= 0.1
      linkbot.setAccelEventThreshold(accelThresh)
      print('Accel threshold set to {}'.format(accelThresh))
