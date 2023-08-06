#!/usr/bin/env python
#-*- coding: utf-8 -*-

import usb
import serial
import os

if os.name == "posix": #GNU/Linux
    os.environ["PORTNAME"] = "/dev/ttyACM%d"

elif os.name == "nt":  #Windows
    os.environ["PORTNAME"] = "COM%d"


########################################################################
class USBtools(object):

    #----------------------------------------------------------------------
    def __init__(self, vboot="v4", timeout=1000):
        super(USBtools, self).__init__()

        """PinguinoUSB([vboot="v4", vendor=0x04D8, product=0xFEAA, timeout=1000, interface=0, endpoint_out=0x01])

        Package for easy comunication with Pinguino boards,

        Parameters
        ----------
        vboot : str
            Booloader version

        Returns
        -------
        PinguinoUSB : object
           Message from Pinguino

        Examples
        --------
        >>> PinguinoUSB()
        >>> PinguinoUSB("v2")
        >>> PinguinoUSB(vboot="v2")
        """

        self.VENDOR = 0x04D8
        self.PRODUCT = 0xFEAA

        self.TIMEOUT = timeout  #1000
        self.INTERFACE = 0
        self.ENDPOINT_OUT = 0x01

        vboot = vboot.lower()
        if vboot == "v2": self.set_boot2()
        elif vboot == "v4": self.set_boot4()
        else:
            raise Exception("Incorrect bootloader version, available: v2, v4")

        self.__connect__()


    #----------------------------------------------------------------------
    def set_boot2(self):
        """Set bootloader V2.

        Set configuration for Pinguino boards with bootloader version 1 or 2.
        """

        self.CONFIGURATION = 0x03
        self.ENDPOINT_IN = 0x82

    #----------------------------------------------------------------------
    def set_boot4(self):
        """set_boot4()

        Set configuration for Pinguino boards with bootloader version 4.
        """

        self.CONFIGURATION = 0x01
        self.ENDPOINT_IN = 0x81

    #----------------------------------------------------------------------
    def __pinguino__(self):
        busses = usb.busses()
        for bus in busses:
            for dev in bus.devices:
                if dev.idVendor == self.VENDOR and dev.idProduct == self.PRODUCT:
                    return dev
        return

    ##----------------------------------------------------------------------
    #def __pinguino__(self):
        #dev = usb.core.find(idVendor=self.VENDOR, idProduct=self.PRODUCT)

        ## was it found?
        #if dev is None:
            #raise ValueError("Device not found")


    ##----------------------------------------------------------------------
    #def open_device(self):
        #try:
            #self.dh = self.pinguino_dev.open()
            #self.dh.setConfiguration(self.CONFIGURATION)
            #self.dh.claimInterface(self.INTERFACE)

            ##if self.dh.is_kernel_driver_active(0) is True:
                ##self.dh.detach_kernel_driver(0)

        #except usb.USBError, V:
            #raise Exception(V[1])



    ##----------------------------------------------------------------------
    #def __connect__(self):
        #try:
            #self.pinguino_dev = self.__pinguino__()
        #except usb.USBError, V:
            #raise Exception(V[1])
        #if self.pinguino_dev is None:
            #raise Exception("No Pinguino devices connected to USB host")

        #self.open_device()


    #----------------------------------------------------------------------
    def __connect__(self):
        pinguino = self.__pinguino__()
        if pinguino is None:
            raise Exception("No Pinguino devices connected to USB host")
        try:
            self.dh = pinguino.open()
            self.dh.setConfiguration(self.CONFIGURATION)
            self.dh.claimInterface(self.INTERFACE)
        except usb.core.USBError, V:
            raise Exception(V[1])

    #----------------------------------------------------------------------
    def write(self, msg):
        """write(str)

        Write str_ on Pinguino,
        if no data connection return Exception.

        Parameters
        ----------
        msg : str
            String to write on Pinguino.

        Examples
        --------
        >>> write("Hola mundo")
        """

        try:
            self.dh.bulkWrite(self.ENDPOINT_OUT, msg, self.TIMEOUT)
        except usb.USBError, V:
            raise Exception(V[1])


    #----------------------------------------------------------------------
    def read(self, length=64):
        """read()

        Return a string with message from Pinguino,
        if no data return Exception.

        Returns
        -------
        read : str
           Message from Pinguino

        Examples
        --------
        >>> read()
        "Pinguino\n"
        """

        try:
            return "".join(map(chr, self.dh.bulkRead(self.ENDPOINT_IN, length, self.TIMEOUT)))
        except usb.core.USBError, V:
            raise Exception(V[1])

########################################################################
class CDCtools(object):

    #----------------------------------------------------------------------
    def __init__(self, port=None, baudrate=9600, timeout=1):
        super(CDCtools, self).__init__()

        """PinguinoCDC([port=None, baudrate=9600, timeout=1])

        Package for easy comunication with Pinguino boards,

        Parameters
        ----------
        vboot : str
            Booloader version

        Returns
        -------
        PinguinoUSB : object
           Message from Pinguino

        Examples
        --------
        >>> PinguinoUSB()
        >>> PinguinoUSB("v2")
        >>> PinguinoUSB(vboot="v2")
        """

        self.TIMEOUT = timeout  #1
        self.BAUDRATE = baudrate  #9600
        self.PORTNAME = os.getenv("PORTNAME")

        list_ports = avalilable_ports()
        if port is None:
            if list_ports:
                self.PORT = list_ports[0]
            else:
                raise Exception("No open ports found or no device connected.")
        else:
            if not port in list_ports:
                raise Exception("Port '%s' is not open or no device connected."%self.PORTNAME%port)
            else: self.PORT = port

        self.__connect__()

    #----------------------------------------------------------------------
    def __connect__(self):
        try:
            self.cdc = serial.Serial(port=self.PORTNAME%self.PORT, timeout=self.TIMEOUT, baudrate=self.BAUDRATE)
        except:
            raise Exception("No CDC devices connected to USB host")

    #----------------------------------------------------------------------
    def write(self, msg):
        """write(str)

        Write str_ on Pinguino,
        if no data connection return Exception.

        Parameters
        ----------
        msg : str
            String to write on Pinguino.

        Examples
        --------
        >>> write("Hola mundo")
        """

        try:
            self.cdc.write(msg)
        except serial.serialutil.SerialException, V:
            raise Exception(V[0])

    #----------------------------------------------------------------------
    def read(self, length=64):
        """read()

        Return a string with message from Pinguino,
        if no data return Exception.

        Returns
        -------
        read : str
           Message from Pinguino

        Examples
        --------
        >>> read()
        "Pinguino\n"
        """

        try:
            return self.cdc.read(length)[:-1]  #slicing for delete last \n pyserial added
        except usb.USBError, V:
            raise Exception(V[0])



#----------------------------------------------------------------------
def avalilable_ports():
    ports = []
    for port in range(30):
        try:
            dev = serial.Serial(os.getenv("PORTNAME")%port)
            ports.append(port)
            dev.close()
        except:
            continue
    return ports
