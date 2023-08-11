#!/usr/bin/env python

import signal

class GracefulKiller:
  kill_now = False
  
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)
    signal.signal(signal.SIGTSTP, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True