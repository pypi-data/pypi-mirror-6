#!/usr/bin/env python
#-*- coding: utf-8 -*-

from .ptools import CDCtools
from .base import PynguinoBase

########################################################################
class PynguinoCDC(CDCtools, PynguinoBase):
    
    def __init__(self, port=None, baudrate=9600, timeout=1):
        super(PynguinoCDC, self).__init__(port, baudrate, timeout)
        
    #----------------------------------------------------------------------
    def close(self):
        self.cdc.close()
        
