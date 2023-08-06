#!/usr/bin/env python
#-*- coding: utf-8 -*-

from .ptools import CDCtools
from .base import PynguinoBase

########################################################################
class PynguinoCDC(CDCtools, PynguinoBase):
    
    def __init__(self, port=0, baudrate=9600):
        super(PynguinoCDC, self).__init__(port, baudrate)
        
    #----------------------------------------------------------------------
    def close(self):
        self.cdc.close()
        
