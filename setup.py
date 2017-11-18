#!/usr/bin/env python

from distutils.core import setup, Extension

__base__ = {
    'name': 'midiio',
    'version': 'v0.0.1',
    'description': 'Python MIDI IO',
    'classifiers': ['Programming Language :: Python',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Development Status :: 4 - Beta',
            'Topic :: Multimedia :: Sound/Audio :: MIDI'],
    'url': 'https://github.com/blowfeld/python-midi-io',
    'maintainer': 'blowfeld',
    'maintainer_email': 'grand.hifi@gmail.com',
    'package_dir': {'midiio':'midiio'},
    'py_modules': ['midiio.containers', 'midiio.__init__', 'midiio.events', 'midiio.eventio', 'midiio.util', 'midiio.fileio', 'midiio.constants'],
    'ext_modules': [],
    'ext_package': '',
    'scripts': ['scripts/mididump.py',],
}

if __name__ == "__main__":
    setup(**__base__.copy())
