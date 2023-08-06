#!/usr/bin/env python

import barobo
import time

if __name__ == "__main__":
  mobot = barobo.mobot.Mobot()
  mobot.connectBluetooth("00:06:66:46:42:41")

  for _ in range(10):
    print(mobot.getJointAngles())
    time.sleep(1)

  mobot.move(90, 0, 0, 90)
