#!/usr/bin/env python

class Lock:

    def __init__(self):
        self._haslock=False

    def acquireLock(self):
        self._haslock=True

    def releaseLock(self):
        self._haslock=False

    def checkLock(self):
        return self._haslock
    
    def doIneedLock(self,git_delete_actions,git_create_actions,git_update_actions):
        return (len(git_delete_actions["folders"])>0 or 
                len(git_delete_actions["dashboards"])>0 or
                len(git_create_actions["folders"])>0 or
                len(git_create_actions["dashboards"])>0 or
                len(git_update_actions["folders"])>0 or
                len(git_update_actions["dashboards"])>0
                )