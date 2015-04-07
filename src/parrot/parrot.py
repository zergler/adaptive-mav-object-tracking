#!/usr/bin/env python2

import cv2
import json
import time

# Local modules.
import camera
import controller

# Igor's modules.
from feature_extraction import hough_transform
from feature_extraction import optical_flow
from tracking import bounding_box
from tracking import cam_shift


class ParrotError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg):
        self.msg = 'Error: %s' % msg

    def print_error(self):
        print(self.msg)


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
        self.init_image = None

    def init_camera(self):
        """ Initializes the camera thread.
        """
        camera_address = 'tcp://' + self.address + ':' + str(self.ports['VIDEO'])
        self.camera = camera.Camera(camera_address)
        self.camera.daemon = True
        self.camera.start()

        # Wait until the camera thread is initialized.
        timeout = time.time() + 15  # max wait is 15 seconds
        while True:
            if self.camera.capturing:
                break
            if time.time() > timeout and not self.camera.capturing:
                raise camera.CameraInitError()

        self.init_image = self.camera.get_image()

    def init_controller(self):
        """ Initializes the controller thread.
        """
        self.controller = controller.Controller()
        self.controller.daemon = True
        self.controller.start()

        # Wait until the controller thread is initialized.
        timeout = time.time() + 15  # max wait is 15 seconds
        while True:
            if self.controller.controlling:
                break
            if time.time() > timeout and not self.controller.controlling:
                raise controller.ControllerInitError()

    def init_receiver(self):
        """ Initializes the receiver thread.
        """
        pass

    def init_feature_extract(self):
        """ Initializes feature extraction. Make sure the camera is initialized
            before calling this function.
        """
        assert self.init_image is not None
        self.feat_opt_flow = optical_flow.OpticalFlow(self.init_image)
        self.feat_hough_trans = hough_transform.HoughTransform()

    def init_tracking(self, bound_box):
        """ Initializes tracking. Make sure the camera is initialized before
            calling this function.
        """
        assert self.init_image is not None
        if bound_box is None:
            raise bounding_box.BoundingBoxError()
        elif len(bound_box) != 2:
            raise bounding_box.BoundingBoxError()
        elif (len(bound_box[0]) != 2) or (len(bound_box[1]) != 2):
            raise bounding_box.BoundingBoxError()
        self.feat_cam_shift = cam_shift.CamShift(self.init_image, bound_box[0], bound_box[1])

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
    parrot.init_camera()

    while True:
        cv2.imshow('Image', parrot.camera.get_image())
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

if __name__ == '__main__':
    import pdb
    test_parrot()
