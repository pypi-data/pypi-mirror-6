#!/usr/bin/env python

import os
import logging

import pyaas

# Set the root for pyaas to this directory
pyaas.util.setroot(os.path.dirname(__file__))

def main():
    pyaas.settings.load()
    pyaas.storage.initialize()

    app = pyaas.server.Application()

    # important to extend if using built-in authentication
    app.patterns.extend([
        ( r'/', pyaas.handlers.Index )
    ])

    try:
        app.Listen()
    except KeyboardInterrupt:
        app.Stop()

if '__main__' == __name__:
    try:
        main()
    except pyaas.error as e:
        logging.critical('%s', e)
