#!/usr/bin/env python2

import pygame
import threading
import numpy as np

""" Remote control module for controlling the drone using a simple gamepad.
    Keyboard presses won't work for executing expert's policies since multiple
    button presses cannot be registered. Also, a gamepad will allow better and
    more fine-tuned control during training.
"""


class RemoteError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg):
        self.msg = 'Error: %s' % msg

    def print_error(self):
        print(self.msg)


class Remote(threading.Thread):
    """ Handles the conversion of gamepad inputs to drone commands.
    """
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        pygame.init()
        self.j = pygame.joystick.Joystick(0)
        self.j.init()

    def run(self):
        i = 0
        while True:
            inputs = self.get()
            self.queue.put(inputs)
            i += 1

    def get(self):
        """ Gets the associated command from the current gamepad inputs.
        """
        axe = np.zeros((1, self.j.get_numaxes()))
        but = np.zeros((1, self.j.get_numbuttons()))
        pygame.event.pump()

        # Read input from the two joysticks.
        for i in range(0, self.j.get_numaxes()):
            axe[0, i] = self.j.get_axis(i)

        # Read input from buttons.
        for i in range(0, self.j.get_numbuttons()):
            but[0, i] = self.j.get_button(i)

        # Regularize the axes for Y.
        axe[0, 1] = -axe[0, 1]
        if abs(axe[0, 1]) < 0.0001:
            axe[0, 1] = 0.0

        # Based on the input, construct the command to be sent to the drone.
        cmd = {
            'X': axe[0, 0],
            'Y': axe[0, 1],
            'Z': axe[0, 3],
            'R': axe[0, 2],
            'C': but[0, 0],
            'T': but[0, 1],
            'L': but[0, 2],
            'S': but[0, 3]
        }
        thresh = 0.001
        if (abs(cmd['X']) < thresh) and (abs(cmd['Y']) < thresh) and (abs(cmd['Z']) < thresh) and (abs(cmd['R']) < thresh):
            cmd['S'] = 1
        return cmd


def _test_remote():
    #pdb.set_trace()
    remote_queue = Queue.Queue(maxsize=1)
    remote = Remote(remote_queue)
    remote.daemon = True
    remote.start()

    # Grab the initial remote data so we know it is initialized.
    while True:
        remote_input = remote_queue.get()
        print(remote_input)
        time.sleep(0.1)

if __name__ == '__main__':
    import pdb
    import time
    import Queue
    _test_remote()
