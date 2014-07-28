#!/usr/bin/env python

"""AKQA BirdHouse"""
#
# Copyright 2014 AKQA
#
# nathan.waddington@akqa.com
#
# This file reads GPIO pin 23 which is being driven by an arduino.
# If the pin is tripped, it plays a sound.
#
# 2014-7-10 adding a mcp3000 to the circut so that the raspberry pi can read analog inputs. Removing the arduino.

# pylint: disable=W0401,W0611,W0614#
from time import sleep
import sys

from mcp3008spi import MCP3008
import RPi.GPIO as GPIO


# globals
DEBUG = 0

# change these as desired - they're the pins connected from the SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

y_pin = 0
x_pin = 1

x = MCP3008(x_pin, SPICLK, SPIMOSI, SPIMISO, SPICS)
y = MCP3008(y_pin, SPICLK, SPIMOSI, SPIMISO, SPICS)


def setup():
    pass


def loop():
    """this is the main loop--this runs forever."""
    while True:  # Go!
        print("x: " + str(x.readadc()) + "\ty: " + str(y.readadc()))
        sleep(0.5)  # wait half a second before reading again


# TODO: figure out where/when/how to push a message to a server.
# TODO: figure out if we need to do an iBeacon transmission here or somewhere else in the OS


def main():
    """main"""
    setup()
    loop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        del x
        del y
        sys.exit("KeyboardInterrupt.")
