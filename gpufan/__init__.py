"""GPUFan helps cooling GPUs inside python code."""

import torch
import multiprocessing as mp
from threading import Lock
from .gpu import GPU


DRIVER_CONTROL = 'driver'
AGGRESSIVE_CONTROL = 'aggressive'
CONSTANT_CONTROL = 'constant'


gpus_in_control_ = {}
prevent_exceptions_ = False
started_ = False
start_lock_ = Lock()


def get_device_id_(device):
    try:
        return device.index or torch.cuda.current_device().index
    except AttributeError:
        return int(device)


class Task(object):
    def __init__(self, command, device_id, *args, **kwargs):
        self.command = command
        self.id = device_id
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return '<Task GPU:{0} command:{1}>'.format(self.id, self.command)


def send_task_(task, device, *args, **kwargs):
    device_id = get_device_id_(device)
    mp_q.put(Task(task, device_id, *args, **kwargs))


def constant(device, percentage):
    start_()
    send_task_(CONSTANT_CONTROL, device, percentage)


def aggressive(device):
    start_()
    send_task_(AGGRESSIVE_CONTROL, device)


def driver(device):
    start_()
    send_task_(DRIVER_CONTROL, device)


def prevent_exceptions():
    prevent_exceptions_ = True


def controller_(q):
    gpus = {}
    while 1:
        task = q.get()
        print(task)

        try:
            gpu = gpus[task.id]
        except KeyError:
            gpu = GPU(task.id)
            gpus[task.id] = gpu

        if task.command == CONSTANT_CONTROL:
            gpu.constant(*task.args)
        elif task.command == AGGRESSIVE_CONTROL:
            gpu.aggressive()
        elif task.command == DRIVER_CONTROL:
            gpu.driver()


mp_ctx = mp.get_context('fork')
mp_q = mp_ctx.Queue()
mp_p = mp_ctx.Process(target=controller_, args=(mp_q,))
mp_p.daemon = True


def start_():
    global started_
    with start_lock_:
        if not started_:
            mp_p.start()
        started_ = True
