#!/usr/bin/env python
#-*- coding: utf-8 -*-

import time

f = lambda n:n

########################################################################
class PynguinoBase(object):
    """"""
    #----------------------------------------------------------------------
    def __init__(self):
        super(PynguinoBase, self).__init__()
        
        self.dict_format_mode = {"INPUT": "INPUT",
                                 "1": "INPUT",
                                 1: "INPUT",
                                 "OUTPUT": "OUTPUT",
                                 "0": "OUTPUT",
                                 0: "OUTPUT",}
        
        self.dict_format_write = {"HIGH": "HIGH",
                                  "1": "HIGH",
                                  1: "HIGH",
                                  "LOW": "LOW",
                                  "0": "LOW",
                                  0: "LOW",}
        


    #----------------------------------------------------------------------
    def pinMode(self, pin, mode):
        mode = self.dict_format_mode.get(mode, None)
        if mode is None:
            raise Exception("Mode value are incorrect")
        self.write("pinMode(%d,%s)"%(pin, mode))
        
    #----------------------------------------------------------------------
    def digitalWrite(self, pin, write):
        write = self.dict_format_write.get(write, None)
        if write is None:
            raise Exception("write value are incorrect")
        self.write("digitalWrite(%d,%s)"%(pin, write))
        
    #----------------------------------------------------------------------
    def digitalRead(self, pin, func=f):
        self.write("digitalRead(%d)"%pin)
        return func(self.read())
    
    #----------------------------------------------------------------------
    def analogWrite(self, pin, write):
        self.write("analogWrite(%d,%s)"%(pin, str(write)))
        
    #----------------------------------------------------------------------
    def analogRead(self, pin, func=f):
        self.write("analogRead(%d)"%pin)
        return func(self.read())
        
    #----------------------------------------------------------------------
    def eepromRead(self, mem, func=f):
        self.write("eepromRead(%d)"%mem)
        return func(self.read())
    
    #----------------------------------------------------------------------
    def eepromWrite(self, mem, value):
        self.write("eepromWrite(%d,%s)"%(mem, str(value)))
        
    #----------------------------------------------------------------------
    def delay(self, ms):
        time.sleep(ms/1e3)
        
    #----------------------------------------------------------------------
    def delayMicroseconds(self, us):
        time.sleep(ms/1e6)
        
    #----------------------------------------------------------------------
    def allOutput(self):
        self.write("allOutput")
        
    #----------------------------------------------------------------------
    def allInput(self):
        self.write("allInput")
        
    #----------------------------------------------------------------------
    def allHigh(self):
        self.write("allHigh")

    #----------------------------------------------------------------------
    def allLow(self):
        self.write("allLow")
        
    #----------------------------------------------------------------------
    def reset(self):
        self.write("reset")

    #----------------------------------------------------------------------
    def check_response(self, key, response):
        self.write(key)
        return self.read() == response