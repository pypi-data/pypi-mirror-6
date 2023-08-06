#!/usr/bin/env python

from barobo import Linkbot, Dongle
import time
import sys
import math

def deg2rad(deg):
  return deg*math.pi/180.0

def rad2deg(rad):
  return rad*180.0/math.pi

def normalizeAngle(rad):
  rad = math.fmod(rad, 2*math.pi)
  if rad > math.pi:
    rad -= math.pi
  return rad

class ParaLinkbot(Linkbot):
  def __init__(self):
    Linkbot.__init__(self)
    self.x = 0
    self.y = 0
    self.theta = 0
    self.wheelbase = 3.75 #inches
    self.wheeldiameter = 3.5 #inches

  def init(self):
    self.angles = self.getJointAngles()
    self.angles = map(deg2rad, self.angles)
    print('Current angles: {}'.format(self.angles))

  def turn(self, theta):
    print('Turning by {}'.format(theta))
    theta = deg2rad(theta)
    basearc = (self.wheelbase/2.0)*theta
    wheelrot = basearc / (self.wheeldiameter/2.0)
    self.angles[0] -= wheelrot
    self.angles[2] -= wheelrot
    self.moveTo(rad2deg(self.angles[0]), 0, rad2deg(self.angles[2]))
    self.theta += theta
    self.theta = normalizeAngle(self.theta)

  def moveDistance(self, inches):
    print('Moving {} inches...'.format(inches))
    theta = inches/(self.wheeldiameter/2.0)
    self.angles[0] += theta
    self.angles[2] -= theta
    self.moveTo(rad2deg(self.angles[0]), 0, rad2deg(self.angles[2]))
    dx = inches*math.cos(self.theta)
    self.x += dx
    dy = inches*math.sin(self.theta)
    self.y += dy

  def goto(self, x, y):
    global_phi = math.atan2(y-self.y, x-self.x)
    d_phi = global_phi - self.theta
    self.turn(rad2deg(d_phi))
    d = math.sqrt( (y-self.y)**2 + (x-self.x)**2)
    self.moveDistance(d)

def func(x):
  return 0.5*x**2

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print ("Usage: {0} <Com_Port> [Linkbot Serial ID]".format(sys.argv[0]))
    quit()
  if len(sys.argv) == 3:
    serialID = sys.argv[2]
  else:
    serialID = None
  dongle = Dongle()
  dongle.connectDongleSFP(sys.argv[1])
  linkbot = dongle.getLinkbot(serialID, linkbotClass=ParaLinkbot)
  linkbot.init()
 
  i = -5
  linkbot.goto(i, func(i))
  linkbot.moveWait()
  print('Start!')
  while i < 5:
    linkbot.goto(i, func(i))
    i += 0.1
    time.sleep(0.1)
