#!/usr/bin/env python

from distutils.core import setup, Extension

__base__ = {
    'name': 'midi',
    'version': 'v0.2.3',
    'description': 'Python MIDI API',
    'author': '',
    'author_email': '',
    'package_dir': {'midi':'src'},
    'py_modules': ['midi.containers', 'midi.__init__', 'midi.events', 'midi.eventio', 'midi.util', 'midi.fileio', 'midi.constants'],
    'ext_modules': [],
    'ext_package': '',
    'scripts': ['scripts/mididump.py',],
}

if __name__ == "__main__":
    setup(**__base__.copy())
