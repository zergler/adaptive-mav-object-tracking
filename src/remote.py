#!/usr/bin/env python2

""" Remote control module.

    Remote control module for controlling the drone using a simple gamepad or
    using the keyboard. Keyboard presses won't work well for executing expert's
    policies since controlling the drone will be harder. A gamepad will allow
    better and more fine-tuned control during training.
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
    """ Handles the conversion of gamepad inputs and keyboard intpus to drone
        commands. This thread runs as long as the pygame module is correctly
        initialized.
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

    #def key_press(self, event):
    #    """ Commands the drone to fly using key presses.
    #    """
    #    char_pressed = event.keysym

    #    # Flying keys (persistent).
    #    if char_pressed == 'd':
    #        if self.fly.verbosity >= 1:
    #            print('Sending command to fly right at speed %0.1f.' % self.fly.speed)
    #        self.fly.drone.fly_right(self.fly.speed)
    #    elif char_pressed == 'a':
    #        if self.fly.verbosity >= 1:
    #            print('Sending command to fly left at speed %0.1f.' % self.fly.speed)
    #        self.fly.drone.fly_left(self.fly.speed)
    #    elif char_pressed == 's':
    #        if self.fly.verbosity >= 1:
    #            print('Sending command to fly backward at speed %0.1f.' % self.fly.speed)
    #        self.fly.drone.fly_backward(self.fly.speed)
    #    elif char_pressed == 'w':
    #        if self.fly.verbosity >= 1:
    #            print('Sending command to fly forward at speed %0.1f.' % self.fly.speed)
    #        self.fly.drone.fly_forward(self.fly.speed)
    #    elif char_pressed == 'q':
    #        if self.fly.verbosity >= 1:
    #            print('Sending command to turn left at speed %0.1f.' % self.fly.speed)
    #        self.fly.drone.turn_left(self.fly.speed)
    #    elif char_pressed == 'e':
    #        if self.fly.verbosity >= 1:
    #            print('Sending command to turn right at speed %0.1f.' % self.fly.speed)
    #        self.fly.drone.turn_right(self.fly.speed)
    #    elif char_pressed == 'r':
    #        if self.fly.verbosity >= 1:
    #            print('Sending command to fly up at speed %0.1f.' % self.fly.speed)
    #        self.fly.drone.fly_up(self.fly.speed)
    #    elif char_pressed == 'f':
    #        if self.fly.verbosity >= 1:
    #            print('Sending command to fly down at speed %0.1f.' % self.fly.speed)
    #        self.fly.drone.fly_down(self.fly.speed)

    #    # Other keys.
    #    elif char_pressed == 't':
    #        if self.fly.verbosity >= 1:
    #            print('Sending command to take off.')
    #        self.fly.drone.takeoff()
    #    elif char_pressed == 'l':
    #        if self.fly.verbosity >= 1:
    #            print('Sending command to land')
    #        self.fly.drone.land()
    #    elif char_pressed == 'c':
    #        if self.fly.verbosity >= 1:
    #            print('Sending command to change camera.')
    #        if self.fly.drone.active_camera == 'FRONT':
    #            self.fly.drone.change_camera('BOTTOM')
    #        else:
    #            self.fly.drone.change_camera('FRONT')
    #    elif char_pressed == ',':
    #        self.fly.speed += 1
    #        if self.fly.verbosity >= 1:
    #            print('Changing speed to %s' + str(self.fly.speed))

    #def key_release(self, event):
    #    """ Commands the drone to stop when the relevant keys are released.
    #    """
    #    char_released = event.keysym
    #    drone_stop_list = ['d', 'a', 's', 'w', 'q', 'e', 'r', 'f']
    #    if char_released in drone_stop_list:
    #        self.drone.stop()



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
