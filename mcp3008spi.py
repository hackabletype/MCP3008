#!/usr/bin/env python
# This file drives an mcp3008 analog to digital converter on the Raspberry Pi
__author__ = 'nathan.waddington@akqa.com'

import RPi.GPIO as GPIO

DEBUG = 0


class MCP3008(object):
    __adcPinsUsed = set()

    def __init__(self, adcnum, clockpin, mosipin, misopin, cspin):
        """MCP3008 Initializer -- set up vars, check for bounds"""

        if DEBUG:
            print("initializing MCP3008 for adc pin {}".format(adcnum))

        if 0 <= adcnum <= 7:
            self._adcnum = adcnum
        else:
            raise InvalidPinSelectionException("adcnum must be between 0-7")

        self._clockpin = clockpin
        self._mosipin = mosipin
        self._misopin = misopin
        self._cspin = cspin

        if len(MCP3008.__adcPinsUsed) == 0:
            if DEBUG:
                print("First instance of MCP3008, initializing SPI pins")
            GPIO.setmode(GPIO.BCM)

            # set up the SPI interface pins
            GPIO.setup(self._mosipin, GPIO.OUT)
            GPIO.setup(self._misopin, GPIO.IN)
            GPIO.setup(self._clockpin, GPIO.OUT)
            GPIO.setup(self._cspin, GPIO.OUT)

        if adcnum in MCP3008.__adcPinsUsed:
            raise SelectedPinInUseException(
                "Pin already used. MCP3008 adc pins currently in use: {}".format(MCP3008.__adcPinsUsed))

        MCP3008.__adcPinsUsed.add(adcnum)
        if DEBUG:
            print("MCP3008 pins in use: {}".format(MCP3008.__adcPinsUsed))


    def readadc(self):
        """ read SPI data from MCP3008 chip, 8 possible adc's (0 through 7).
            this fn is based on code from Mikey Sklar's article:
            https://learn.adafruit.com/reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi/script """

        GPIO.output(self._cspin, True)

        GPIO.output(self._clockpin, False)  # start clock low
        GPIO.output(self._cspin, False)  # bring CS low

        commandout = self._adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3  # we only need to send 5 bits here
        for i in range(5):
            if commandout & 0x80:
                GPIO.output(self._mosipin, True)
            else:
                GPIO.output(self._mosipin, False)
            commandout <<= 1
            GPIO.output(self._clockpin, True)
            GPIO.output(self._clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
            GPIO.output(self._clockpin, True)
            GPIO.output(self._clockpin, False)
            adcout <<= 1
            if GPIO.input(self._misopin):
                adcout |= 0x1

        GPIO.output(self._cspin, True)

        adcout >>= 1  # first bit is 'null' so drop it
        return adcout


    def __del__(self):
        if DEBUG:
            print("deleting MCP3008 instance {}".format(self._adcnum))
        if len(MCP3008.__adcPinsUsed) > 0:  # remove the current pin from the pinused set
            if DEBUG:
                print("removing adc pin: {}".format(self._adcnum))
            MCP3008.__adcPinsUsed.remove(self._adcnum)
            if DEBUG:
                print("adc pins remaining: {}".format(MCP3008.__adcPinsUsed))

        if len(MCP3008.__adcPinsUsed) == 0:  # Cleanup the GPIO b/c we aren't using the pins anymore
            if DEBUG:
                print("Last adc pin removed, cleaning up GPIO")
            GPIO.cleanup()


class InvalidPinSelectionException(Exception):
    pass


class SelectedPinInUseException(Exception):
    pass
