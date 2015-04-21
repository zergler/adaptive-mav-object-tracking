#!/usr/bin/env python2

""" Remote control module.

    Remote control module for controlling the drone using a simple gamepad.
    Keyboard presses won't work for executing expert's policies since multiple
    button presses cannot be registered. Also, a gamepad will allow better and
    more fine-tuned control during training.
"""

import pygame
import threading
import sys
import numpy as np


class RemoteError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg='', warning=False):
        default_header = 'Error: remote'
        default_error = '%s: an exception occured.' % default_header
        self.msg = default_error if msg == '' else '%s: %s.' % (default_header, msg)
        self.warning = warning

    def print_error(self):
        print(self.msg)


class Remote(threading.Thread):
    """ Handles the conversion of gamepad inputs to drone commands. This thread
        runs as long as the pygame module is correctly initialized.
    """
    def __init__(self, queue, bucket):
        threading.Thread.__init__(self)
        self.queue = queue    # the queue that stores commands from remote
        self.bucket = bucket  # the queue that stores exceptions from the thread

        # Flags for errors.
        self.pygame_okay = False
        self.joystick_okay = False

        # Initialize pygame.
        (_, numfail) = pygame.init()
        if numfail > 0:
            self.bucket.put(RemoteError('pygame initialization failed'))
            return

        self.pygame_okay = True
        self.j = None

    def run(self):
        try:
            if self.pygame_okay:
                while True:
                    self.check_joystick_okay()
                    if self.joystick_okay:
                        inputs = self.get()
                        self.queue.put(inputs)
        except:
            exc_error = sys.exc_info()
            remote_error = RemoteError('%s, %s, %s' % exc_error)
            self.bucket.put(remote_error)

    def check_joystick_okay(self):
        """ Makes sure the joystick is running okay.
        """
        # Check that the joystick is still running.
        if not pygame.joystick.get_count():

            # Block until the joystick is reconnected.
            while not pygame.joystick.get_count():
                pass

            # Once it's reconnected, reinitialize it.
            self.j = pygame.joystick.Joystick(0)
            self.okay = self.j.get_init()

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
    pdb.set_trace()
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
