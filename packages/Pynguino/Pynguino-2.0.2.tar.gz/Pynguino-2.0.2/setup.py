#!/usr/bin/env python
#-*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name = "Pynguino",
      version = "2.0.2",
      description = "Easy interface Pinguino-Python",
      description_file = "README.rst", 
      
      author = "Yeison Cardona",
      author_email = "yeison.eng@gmail.com",
      maintainer = "Yeison Cardona",
      maintainer_email = "yeison.eng@gmail.com",
      
      url = "https://bitbucket.org/YeisonEng/pynguino-2.0", 
      download_url = "https://bitbucket.org/YeisonEng/pynguino-2.0/downloads",
      
      license = "BSD 3-Clause",
      install_requires = ["pyusb==1.0.0b1", "pyserial"],
      keywords = 'microchip, electronic, pinguino',
      #platforms = ["all"], 
      
      classifiers=[#list of classifiers in https://pypi.python.org/pypi?:action=list_classifiers
                   "Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License", 
                   "Programming Language :: Python",
                   "Topic :: Scientific/Engineering",
                   "Topic :: Software Development :: Libraries",
                   
                   ], 
      
      packages = find_packages(), 
      )