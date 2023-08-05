
#coding:utf-8

import os
from threading import Timer
import socket
import sys
import requests
from datetime import datetime

class Heartbeat(object):
    def __init__(self, interval=60):
        self._quit = None
        self._interval = interval 
 
    def quit(self, func):
        self._quit = func
        return func

    def is_alive(self, func):
        def _():
            if not func():
                if self._quit is not None:
                    self._quit()
                os.kill(os.getpid(), 9)
            else:
                Timer(self._interval, _).start()
        Timer(self._interval+60, _).start()
        return _ 

heartbeat = Heartbeat(5)

