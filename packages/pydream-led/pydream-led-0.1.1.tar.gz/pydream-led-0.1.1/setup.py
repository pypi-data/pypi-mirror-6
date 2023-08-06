#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='pydream-led',
      version='0.1.1',
      description='PyDream - driver for Dream Cheeky 21x7 LED display (VendorId: 0x1d34 DeviceId: 0x001',
      author='Darren P Meyer',
      author_email='darren@darrenpmeyer.com',
      url='https://github.com/darrenpmeyer/pydream-led',
      packages=['pydream'],
      install_requires=[
          'pyusb',
      ],
     )