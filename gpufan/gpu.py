"""This module contains GPU object.

A GPU representes an physical gpu based on its index in the list of
available gpus.
"""
from threading import Thread, Event

from .utils import exec_command
from .curve import Curve
import subprocess as sb
import time


class GPU(object):
    """GPU is a representation of a physical gpu based on its index in the list of available gpus.

    Arguments
    ---------
    device_id int : Index of the GPU
    prevent_exceptions boolean : Silent exceptions
    display str : X display identifier
    """

    def __init__(self, device_id, prevent_exceptions, display=":0"):  # noqa: D107
        self.id = device_id
        self.display = display
        self.check_exceptions = not prevent_exceptions
        self._stop = Event()
        self._thread = None

    def stop(self):
        """Signal the thread to stop execution."""
        self._stop.set()

    @property
    def stopped(self):
        """Check if stopping execution is requested."""
        return self._stop.isSet()

    def __setSpeed(self, speed):
        cmd = [
                "nvidia-settings",
                "-c {0}".format(self.display),
                "-a [gpu:{0}]/GPUFanControlState=1".format(self.id),
                "-a [fan:{0}]/GPUTargetFanSpeed={1}".format(self.id, speed)
        ]
        # using sb.run(cmd, ...) did not work! I guess there is a conflict in -c switch.
        sb.run(" ".join(cmd), shell=True, stdout=sb.DEVNULL, stderr=sb.DEVNULL, check=self.check_exceptions)

    def __customCurveSpeed(self):
        curve = Curve()
        while not self.stopped:
            current_temp = self.__getTemp()
            new_fan_speed = curve.evaluate(current_temp)
            self.__setSpeed(new_fan_speed)
            time.sleep(1.0)

    def __thread_alive(self):
        if self._thread and self._thread.is_alive():
            return True
        return False

    def __getTemp(self):
        """Get temperature of the GPU."""

        command = "nvidia-smi -i %d --query-gpu=temperature.gpu --format=csv,noheader" % self.id
        temperature = exec_command(command).strip()

        return int(temperature)

    def constant(self, percentage):
        """Set a constant fan speed.

        Arguments
        ---------
        percentage int : An integer from 0 to 100
        """
        if self.__thread_alive():
            self.stop()
            self._thread.join()
        self.__setSpeed(percentage)

    def aggressive(self):
        """Control GPU fan based on an aggressive regime.

        It tries to set GPU fan to a high speed as soon as temperature rises.
        """
        if self.__thread_alive():
            return
        self._thread = Thread(target=self.__customCurveSpeed)
        self._thread.daemon = True
        self._thread.start()

    def driver(self):
        """Return control of fan speed to the driver."""
        if self.__thread_alive():
            self.stop()
            self._thread.join()

        cmd = [
                "nvidia-settings",
                "-c {0}".format(self.display),
                "-a [gpu:{0}]/GPUFanControlState=0".format(self.id)
        ]
        sb.run(" ".join(cmd), shell=True, stdout=sb.DEVNULL, stderr=sb.DEVNULL, check=self.check_exceptions)

    def __del__(self):
        """Make sure thread is stopped before destruction."""
        if self.__thread_alive():
            self._thread.stop()
            self._thread.join()
        self.driver()
