#!/usr/bin/env python2

""" Remote control module.

    Remote control module for controlling the drone using a simple gamepad or
    using the keyboard. Keyboard presses won't work well for executing expert's
    policies since controlling the drone will be harder. A gamepad will allow
    better and more fine-tuned control during training.
"""

import debug
import threading
import pygame
import sys
import time
import numpy as np


class Remote(threading.Thread):
    """ Handles the conversion of gamepad inputs and keyboard intpus to drone
        commands. This thread runs as long as the pygame module is correctly
        initialized.
    """
    def __init__(self, debug_queue, error_queue, queue, remote_rate):
        threading.Thread.__init__(self)
        self.debug_queue = debug_queue
        self.error_queue = error_queue
        self.queue = queue
        self.remote_rate = remote_rate

        # Flags for errors.
        self.pygame_okay = False
        self.gamepad_okay = False

        # The default command that is sent to the drone.
        self.default_speed = 0.3
        self.default_cmd = {
            'X': 0.0,
            'Y': 0.0,
            'Z': 0.0,
            'R': 0.0,
            'C': 0,
            'T': False,
            'L': False,
            'S': False
        }
        self.key_flag = False
        self.game_flag = False

        # The keys that should issue a stop command when released.
        self.stop_list = [pygame.K_d, pygame.K_a, pygame.K_s, pygame.K_w, pygame.K_q, pygame.K_e, pygame.K_r, pygame.K_f]

        # Initialize pygame.
        (_, numfail) = pygame.init()
        if numfail > 0:
            self.error_queue.put(debug.Error('remote', 'pygame initialization failed'))
            return
        
        pygame.display.set_mode((100, 100))
        self.pygame_okay = True
        self.gamepad = None
        self.check_gamepad_okay()

    def run(self):
        try:
            if self.pygame_okay:
                while True:
                    # Get the keyboard input.
                    inputs_remote = self.get_keyboard()

                    # Replace the keyboard input with gamepad input if a gamepad
                    # is connected.
                    self.check_gamepad_okay()
                    if self.gamepad_okay and not self.key_flag:
                        #inputs_remote = self.get_gamepad()
                        pass
                    if inputs_remote is not None:
                        self.queue.put(inputs_remote)
                    time.sleep(1.0/self.remote_rate)
        except:
            exc_error = sys.exc_info()
            remote_error = debug.Error('remote', '%s, %s, %s' % exc_error)
            self.error_queue.put(remote_error)

    def check_gamepad_okay(self):
        """ Makes sure the gamepad is running okay.
        """
        # Check that the gamepad is still running.
        if pygame.joystick.get_count():
            if not self.gamepad_okay:
                # Once it's reconnected, reinitialize it.
                self.gamepad = pygame.joystick.Joystick(0)
                self.gamepad.init()
                self.gamepad_okay = self.gamepad.get_init()
        else:
            self.gamepad_okay = False

    def get_gamepad(self):
        """ Gets the associated command from the current gamepad inputs.
        """
        axe = np.zeros((1, self.gamepad.get_numaxes()))
        but = np.zeros((1, self.gamepad.get_numbuttons()))
        pygame.event.pump()

        # Read input from the two gamepads.
        for i in range(0, self.gamepad.get_numaxes()):
            axe[0, i] = self.gamepad.get_axis(i)

        # Read input from buttons.
        for i in range(0, self.gamepad.get_numbuttons()):
            but[0, i] = self.gamepad.get_button(i)

        # Regularize the axes for Y.
        axe[0, 1] = -axe[0, 1]
        if abs(axe[0, 1]) < 0.0001:
            axe[0, 1] = 0.0

        axe[0, 3] = -axe[0, 3]
        if abs(axe[0, 3]) < 0.0001:
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
            # Only send the stop command once.
            if self.game_flag:
                self.game_flag = False
                cmd['S'] = 1
        else:
            self.game_flag = True
        return cmd

    def get_keyboard(self):
        cmd = None
        for event in pygame.event.get():
            # If a key has been pressed down, send the command to the drone.
            if event.type == pygame.KEYDOWN:
                self.key_flag = True
                if event.key == pygame.K_d:
                    cmd = self.fly_right(self.default_speed)
                elif event.key == pygame.K_a:
                    cmd = self.fly_left(self.default_speed)
                elif event.key == pygame.K_s:
                    cmd = self.fly_backward(self.default_speed)
                elif event.key == pygame.K_w:
                    cmd = self.fly_forward(self.default_speed)
                elif event.key == pygame.K_q:
                    cmd = self.turn_left(self.default_speed)
                elif event.key == pygame.K_e:
                    cmd = self.turn_right(self.default_speed)
                elif event.key == pygame.K_r:
                    cmd = self.fly_up(self.default_speed)
                elif event.key == pygame.K_f:
                    cmd = self.fly_down(self.default_speed)
                elif event.key == pygame.K_t:
                    cmd = self.takeoff()
                elif event.key == pygame.K_l:
                    cmd = self.land()

            # If the 'right' key has been released, send the stop command to the
            # drone.
            elif event.type == pygame.KEYUP:
                self.key_flag = False
                if event.key in self.stop_list:
                    cmd = self.stop()
        return cmd

    def land(self):
        cmd = self.default_cmd.copy()
        cmd['L'] = True
        self.debug_queue.put({'MSG': 'Sending command to land.', 'PRIORITY': 1})
        return cmd

    def takeoff(self):
        cmd = self.default_cmd.copy()
        cmd['T'] = True
        self.debug_queue.put({'MSG': 'Sending command to takeoff.', 'PRIORITY': 1})
        return cmd

    def stop(self):
        cmd = self.default_cmd.copy()
        cmd['S'] = True
        self.debug_queue.put({'MSG': 'Sending command to stop.', 'PRIORITY': 0})
        return cmd

    def turn_left(self, speed):
        cmd = self.default_cmd.copy()
        cmd['R'] = -speed
        self.debug_queue.put({'MSG': 'Sending command to turn left at speed %0.1f.' % self.default_speed, 'PRIORITY': 1})
        return cmd

    def turn_right(self, speed):
        cmd = self.default_cmd.copy()
        cmd['R'] = speed
        self.debug_queue.put({'MSG': 'Sending command to turn right at speed %0.1f.' % self.default_speed, 'PRIORITY': 1})
        return cmd

    def fly_up(self, speed):
        cmd = self.default_cmd.copy()
        cmd['Z'] = speed
        self.debug_queue.put({'MSG': 'Sending command to fly up at speed %0.1f.' % self.default_speed, 'PRIORITY': 1})
        return cmd

    def fly_down(self, speed):
        cmd = self.default_cmd.copy()
        cmd['Z'] = -speed
        self.debug_queue.put({'MSG': 'Sending command to fly down at speed %0.1f.' % self.default_speed, 'PRIORITY': 1})
        return cmd

    def fly_forward(self, speed):
        cmd = self.default_cmd.copy()
        cmd['Y'] = speed
        self.debug_queue.put({'MSG': 'Sending command to fly forward at speed %0.1f.' % self.default_speed, 'PRIORITY': 1})
        return cmd

    def fly_backward(self, speed):
        cmd = self.default_cmd.copy()
        cmd['Y'] = -speed
        self.debug_queue.put({'MSG': 'Sending command to fly backward at speed %0.1f.' % self.default_speed, 'PRIORITY': 1})
        return cmd

    def fly_left(self, speed):
        cmd = self.default_cmd.copy()
        cmd['X'] = -speed
        self.debug_queue.put({'MSG': 'Sending command to fly left at speed %0.1f.' % self.default_speed, 'PRIORITY': 1})
        return cmd

    def fly_right(self, speed):
        cmd = self.default_cmd.copy()
        cmd['X'] = speed
        self.debug_queue.put({'MSG': 'Sending command to fly right at speed %0.1f.' % self.default_speed, 'PRIORITY': 1})
        return cmd

    def change_camera(self, camera):
        cmd = self.default_cmd.copy()
        cmd['C'] = camera
        self.debug_queue.put({'MSG': 'Sending command to change the camera.', 'PRIORITY': 1})
        return cmd


def _test_remote():
    pdb.set_trace()
    
    # Set up debug.
    verbosity = 1
    error_queue = Queue.Queue()
    debug_queue = Queue.Queue()
    debugger = debug.Debug(verbosity, debug_queue, error_queue)

    # Set up remote.
    remote_rate = 1
    remote_queue = Queue.Queue(maxsize=1)
    remote = Remote(debug_queue, error_queue, remote_queue, remote_rate)
    remote.daemon = True
    remote.start()

    # Grab the initial remote data so we know it is initialized.
    while True:
        try:
            remote_input = remote_queue.get(block=False)
            print(remote_input)
        except Queue.Empty:
            pass
        try:
            debugger.debug()
            time.sleep(0.1)
        except debug.Error as e:
            e.print_error()
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == '__main__':
    import pdb
    import time
    import Queue
    _test_remote()
