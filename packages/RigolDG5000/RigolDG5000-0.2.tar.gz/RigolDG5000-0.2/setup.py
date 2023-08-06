# -*- coding: latin-1 -*-
import sys

#from distutils.core import setup
from setuptools import setup

long_description=u'''\
Overview
--------

This package can be used to drive a Rigol DG5000 waveform generator. It provides an object oriented interface
to the SCPI commands using Python properties. Especially it does the conversion from number to string (and vice versa) automatically. 

Installation
------------

You need to install the pyvisa package. On windows the pyvisa a package is supported by the `python(x,y) <http://code.google.com/p/pythonxy/>`_ distribution.

To install the RigolDG5000 driver, download the package and run the command ::

   python setup.py install

You can also directly move the RigolDG5000 to a location
that Python can import from (directory in which scripts
using PyDAQmx are run, etc.)

Usage
-----

First you need to create your visa instrument. ::

    inst = visa.instrument('USB0::0x0000::0x0000::DG5Axxxxxxxxx::INSTR', term_chars='\n', timeout=1)
    rigol = RigolDG5000(inst=inst)

    rigol.source[1].load = 50
    rigol.source[1].voltage.unit = "DBM"
    rigol.source[1].frequency.fixed = 10000000
    rigol.source[1].state = 'ON'

    print source[1].frequency.fixed

All the commands are Python properties that can be read or write. 


Contact
-------

Please send bug reports or feedback to `Pierre Cladé`_.


.. _Pierre Cladé: mailto:pierre.clade@spectro.jussieu.fr
'''


setup(name="RigolDG5000", version='0.2',
      author=u'Pierre Cladé', author_email="pierre.clade@spectro.jussieu.fr",
      maintainer=u'Pierre Cladé',
      maintainer_email="pierre.clade@spectro.jussieu.fr",
      license='''\
This software can be used under one of the following two licenses: \
(1) The BSD license. \
(2) Any other license, as long as it is obtained from the original \
author.''',

      description='Interface to the Rigol DG5000 waveform generator',
      long_description = long_description,  
      keywords=['Rigol','DG5000'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'], 
     requires=['pyvisa'],
     packages=["RigolDG5000", ]
)
