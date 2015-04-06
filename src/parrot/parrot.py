#!/usr/bin/env python2

import cv2
import json
import subprocess

# Local modules.
import camera
import controller
import receiver


class Error(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg):
        self.msg = 'Error: %s' % msg

    def print_error(self):
        print(self.msg)


class ArgumentError(Error):
    def __init__(self, arg):
        self.msg = "Error: argument '%s' is invalid." % arg


class Parrot(object):
    """ Encapsulates the AR Parrot Drone 2.0.

        Allows access to the drone's front and bottom cameras, the ability to
        send commands, and the ability to read the dron's navigation data.
    """
    def __init__(self):
        self.default_cmd = {
            'X': 0.0,
            'Y': 0.0,
            'R': 0.0,
            'C': 0,
            'T': False,
            'L': False,
            'S': False
        }
        self.address = '192.168.1.1'
        self.ports = {
            'NAVDATA': 5554,
            'VIDEO':   5555,
            'CMD': 5556
        }
        self.cameras = {
            'FRONT':  0,
            'BOTTOM': 3,
            'CUSTOM': 4
        }
        self.active_camera = self.cameras['FRONT']

    def init_network(self):
        #subprocess.call(['./drone-net.sh', ''])
        pass

    def init_camera(self, parrot_address, video_port):
        """ Initializes the camera thread.
        """
        camera_address = 'tcp://' + parrot_address + ':' + str(video_port)
        self.camera = camera.Camera(camera_address)
        self.camera.daemon = True
        self.camera.start()

    def init_controller(self):
        """ Initializes the controller thread.
        """
        self.controller = controller.Controller()
        self.controller.daemon = True
        self.controller.start()

    def init_receiver(self, parrot_address, navdata_port):
        """ Initializes the receiver thread.
        """
        pass

    def get_navdata(self, query):
        """ Receives the drone's navigation data specified in the query.
        """
        pass

    def exit(self):
        """ Before exiting, safely lands the drone and closes all processes.
        """
        land()

    def land(self):
        cmd = self.default_cmd.copy()
        cmd['L'] = True
        cmd_json = json.dumps(cmd)
        self.controller.send_cmd(cmd_json)

    def takeoff(self):
        cmd = self.default_cmd.copy()
        cmd['T'] = True
        cmd_json = json.dumps(cmd)
        self.controller.send_cmd(cmd_json)

    def stop(self):
        cmd = self.default_cmd.copy()
        cmd = self.default_cmd.copy()
        cmd['S'] = True
        cmd_json = json.dumps(cmd)
        self.controller.send_cmd(cmd_json)

    def turn_left(self, speed):
        cmd = self.default_cmd.copy()
        cmd['R'] = -speed
        cmd_json = json.dumps(cmd)
        self.controller.send_cmd(cmd_json)

    def turn_right(self, speed):
        cmd = self.default_cmd.copy()
        cmd['R'] = speed
        cmd_json = json.dumps(cmd)
        self.controller.send_cmd(cmd_json)

    def fly_up(self, speed):
        cmd = self.default_cmd.copy()
        cmd['Z'] = speed
        cmd_json = json.dumps(cmd)
        self.controller.send_cmd(cmd_json)

    def fly_down(self, speed):
        cmd = self.default_cmd.copy()
        cmd['Z'] = -speed
        cmd_json = json.dumps(cmd)
        self.controller.send_cmd(cmd_json)

    def fly_forward(self, speed):
        cmd = self.default_cmd.copy()
        cmd['Y'] = speed
        cmd_json = json.dumps(cmd)
        self.controller.send_cmd(cmd_json)

    def fly_backward(self, speed):
        cmd = self.default_cmd.copy()
        cmd['Y'] = -speed
        cmd_json = json.dumps(cmd)
        self.controller.send_cmd(cmd_json)

    def fly_left(self, speed):
        cmd = self.default_cmd.copy()
        cmd['X'] = -speed
        cmd_json = json.dumps(cmd)
        self.controller.send_cmd(cmd_json)

    def fly_right(self, speed):
        cmd = self.default_cmd.copy()
        cmd['X'] = speed
        cmd_json = json.dumps(cmd)
        self.controller.send_cmd(cmd_json)

    def change_camera(self, camera):
        cmd['C'] = camera
        cmd = self.fly.default_cmd.copy()
        cmd_json = json.dumps(cmd)
        self.controller.send_cmd(cmd_json)


def test_parrot():
    """ Tests the parrot module
    """
    pdb.set_trace()
    parrot = Parrot()
    parrot.init_network()
    parrot.init_camera(parrot.address, parrot.ports['VIDEO'])

    while True:
        cv2.imshow('Image', parrot.camera.get_image())
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break


if __name__ == '__main__':
    import pdb
    test_parrot()
