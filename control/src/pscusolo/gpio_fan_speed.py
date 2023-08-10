"""GPIO fan speed measurement for the PSCUsolo.

This module implements classes to measure PSCUsolo fan speeds via GPIO input pins connected to the
tachometer output of the fan. This is implemented via the event detection mechanism provided by the
Adafruit_BBIO GPIO class. A callback counts rising edges on the tacho input - a periodic call to
the update() method calculates the the instantaneous and rolling mean freqeuency of the pulese.
Methods convert these to RPM assuming the typical 2 tacho pulses per revolution.

Tim Nicholls, STFC Detector System Software Group
"""
import time
from collections import deque
from typing import Optional

import Adafruit_BBIO.GPIO as GPIO


class RollingMean(deque):
    """Simple rolling mean class.

    This class implements a simple rolling mean calculation for a specified number of samples.
    Based on the standard deque, new values can simply be append()-ed to the object, and the mean
    is calculated based on the number of samples held, i.e. is valid for the first n samples before
    the deque is filled. Successive append() calls will remove the oldest value from the deque.
    """

    def __init__(self, maxlen: int):
        """Initialise the rolling mean.

        This constructor initialises a rolling mean object of the specified length.

        :param maxlen: maximum length of the rolling mean.
        """
        super().__init__([], maxlen=maxlen)

    @property
    def mean(self):
        """Return the current rolling mean.

        This property method calculates and returns the current mean of the values held in the
        object. If no values have been appended, the mean is returned as zero.

        :return: mean of the current values in the object
        """
        mean = 0.0
        if len(self):
            mean = float(sum(self)) / len(self)

        return mean


class GpioFanSpeed:
    """GPIO fan speed measurement class.

    This class implements measurement of fan speeds via GPIO pins connected to the tachometer
    output of fans.
    """

    def __init__(
        self,
        tach_pin: str,
        pwm_pin: Optional[str] = None,
        edge: int = GPIO.RISING,
    ):
        """Initialise the GPIO fan speed object.

        This constructor initialises the GPIO fan speed object. The specified tacho GPIO pin is
        configured as an input and for edge detection. If a PWM pin is specified that is set up as
        desired.

        :param tach_pin : fan tachometer GPIO pin name (using Adafruit_BBIO naming convention)
        :param pwm_pin : optional fan PWM control GPIO pin name
        :param edge : optional edge to detec, defaults to rising edge
        """
        self.tach_pin = tach_pin
        self.pwm_pin = pwm_pin

        # Initialise state of internal counters
        self.event_count = 0
        self.last_count = 0
        self.delta = 0
        self.last_time: Optional[float] = None

        # Initialise frequency variables
        self.freq_1 = 0.0
        self.freq_5 = RollingMean(5)
        self.freq_10 = RollingMean(10)

        # If the PWM pin is specified, enable it as an output. For now set the initial default value
        # to high.
        if self.pwm_pin:
            GPIO.setup(self.pwm_pin, GPIO.OUT, initial=GPIO.HIGH)

        # Set up the tacho pin as an input and add edge event detection
        GPIO.setup(self.tach_pin, GPIO.IN)
        GPIO.add_event_detect(self.tach_pin, edge, self._callback)

    def _callback(self, _: str) -> None:
        """Call back on edge event detection.

        This method is called back when an edge detection event occurs on the tacho pin. The
        event counter is simply incremented.

        :param _ : unused channel argument required by the GPIO callback mechanism
        """
        self.event_count += 1

    def update(self) -> None:
        """Update fan speed calculations.

        This method should be called periodically, e.g. by a background update loop in an adapter,
        to update current fan speed readings. Based on the event counter, this calculates and stores
        the current fan frequency (in Hz) and appends the value to the rolling 5- and 10-sample
        means.
        """
        # Copy the current count locally for consistency and save the current time
        current_count = self.event_count
        now = time.time()

        # Calculate the event count delta
        self.delta = current_count - self.last_count

        # If a previous update has been done, calculate and store the frequency and append to the
        # rolling means.
        if self.last_time:
            self.freq_1 = self.delta / (now - self.last_time)
            self.freq_5.append(self.freq_1)
            self.freq_10.append(self.freq_1)

        # Store the last count and time
        self.last_count = current_count
        self.last_time = now

    @staticmethod
    def freq_to_rpm(freq: float) -> int:
        """Convert frequency to RPM.

        This static method converts a frequency measurement into RPM, assuming the standard two
        pulses per revolution operation of the fan.

        :param freq: frequency to convert
        :return: integer RPM value
        """
        return int(freq * 30)

    @property
    def rpm(self) -> int:
        """Return the current fan speed in RPM.

        This property method returns the current fan speed as RPM. The value is rounded to integer
        to remove the pulse sampling quantisation.

        :return current fan speed in RPM
        """
        return self.freq_to_rpm(self.freq_1)

    @property
    def rpm_5(self) -> int:
        """Return the current 5-sample rolling mean fan speed in RPM.

        This property method returns the current fan speed as RPM from the 5-sample rolling mean.
        The value is rounded to integer to remove the pulse sampling quantisation.

        :return current 5-sample rolling average fan speed in RPM
        """
        return self.freq_to_rpm(self.freq_5.mean)

    @property
    def rpm_10(self) -> int:
        """Return the current 10-sample rolling mean fan speed in RPM.

        This property method returns the current fan speed as RPM from the 10-sample rolling mean.
        The value is rounded to integer to remove the pulse sampling quantisation.

        :return current 10-sample rolling average fan speed in RPM
        """
        return self.freq_to_rpm(self.freq_10.mean)
