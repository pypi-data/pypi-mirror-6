#!/usr/bin/env python
#-*- coding: utf-8 -*-

from .ptools import USBtools
from .base import PynguinoBase

########################################################################
class PynguinoUSB(USBtools, PynguinoBase):
    
    def __init__(self, vboot="v4"):
        super(PynguinoUSB, self).__init__(vboot)