#!/usr/bin/env python

from distutils.core import setup

setup(name='USBArm',
      version='1.0',
      maintainer='InverseSandwich',
      url='http://github.com/inversesandwich/USBArm',
      description = ("A simple to use Python module for controlling USB robotic arm devices on Linux PCs, including the Raspberry Pi."),
      license = "Public Domain",
      package_dir={'usbarm': 'src'},
      packages=['usbarm'],
      install_requires=['pyusb'],
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Operating System :: POSIX :: Linux",
    	],
     )