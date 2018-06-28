"""This module contains GPU object.

A GPU representes an physical gpu based on its index in the list of
available gpus.
"""
from threading import Thread, Event
from subprocess import Popen, PIPE
from .curve import Curve
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetTemperature, NVML_TEMPERATURE_GPU
import time


class GPU(object):
    """GPU is a representation of a physical gpu based on its index in the list of available gpus.

    Arguments
    ---------
    device_id int : index of the GPU
    """

    def __init__(self, device_id):  # noqa: D107
        self.id = device_id
        self._stop = Event()
        self._thread = None

    def stop(self):
        """Signal the thread to stop execution."""
        self._stop.set()

    def stopped(self):
        """Check if stopping execution is requested."""
        return self._stop.isSet()

    def __setSpeed(self, speed):
        process = Popen("nvidia-settings -a [gpu:{0}]/GPUFanControlState=1 -a [fan:{0}]/GPUTargetFanSpeed={1}".format(self.id, speed), shell=True, stdin=PIPE, stdout=PIPE, env={'DISPLAY':':0'})
        process.wait()
        if process.returncode != 0:
            raise Exception("Could not set fan speed")

    def __customCurveSpeed(self):
        nvmlInit()
        self._handle = nvmlDeviceGetHandleByIndex(self.id)
        curve = Curve()
        while(not self.stopped()):
            current_temp = self._getTemp()
            print(current_temp)
            new_fan_speed = curve.evaluate(current_temp)
            self.__setSpeed(new_fan_speed)
            time.sleep(1.0)

    def __thread_alive(self):
        if self._thread and self._thread.is_alive():
            return True
        return False

    def _getTemp(self):
        """Get temperature of the GPU."""
        return nvmlDeviceGetTemperature(self._handle, NVML_TEMPERATURE_GPU)

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
        self.thread = Thread(target=self.__customCurveSpeed)
        self.thread.daemon = True
        self.thread.start()

    def driver(self):
        """Return control of fan speed to the driver."""
        if self.__thread_alive():
            self.stop()
            self.thread.join()
        process = Popen("nvidia-settings -a [gpu:{0}]/GPUFanControlState=0".format(self.id), shell=True, stdin=PIPE, stdout=PIPE, env={'DISPLAY':'0.'})
        process.wait()
        if process.returncode != 0:
            raise Exception("Problem occurred")

    def __del__(self):
        """Make sure thread is stopped before destruction."""
        if self.__thread_alive():
            self.thread.stop()
            self.thread.join()
            self.driver()
