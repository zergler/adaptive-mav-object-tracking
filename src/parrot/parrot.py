#!/usr/bin/env python2

import cv2
import json
import numpy as np
import Queue


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
        self.image = None

        # Feature extraction parameters.
        self.window_size = (15, 7)
        self.overlap = 0.5

    def init_camera(self):
        """ Initializes the camera thread.
        """
        camera_address = 'tcp://' + self.address + ':' + str(self.ports['VIDEO'])
        self.image_queue = Queue.Queue()
        self.camera = camera.Camera(camera_address, self.image_queue)
        self.camera.daemon = True
        self.camera.start()

        self.image = self.image_queue.get()

    def init_controller(self):
        """ Initializes the controller thread.
        """
        self.controller = controller.Controller()
        self.controller.daemon = True
        self.controller.start()

    def init_receiver(self):
        """ Initializes the receiver thread.
        """
        pass

    def init_feature_extract(self):
        """ Initializes feature extraction. Make sure the camera is initialized
            before calling this function.
        """
        assert self.image is not None

        # Grab an example window from the initial image to feed the feature extractors.
        windows = camera.Camera.get_windows(self.image, self.window_size, self.overlap)
        small_image = self.image[windows[0][0][2]:windows[0][0][3], windows[0][0][0]:windows[0][0][1]]

        self.feat_opt_flow = optical_flow.OpticalFlow(small_image)
        self.feat_hough_trans = hough_transform.HoughTransform()

    def init_tracking(self, bound_box):
        """ Initializes tracking. Make sure the camera is initialized before
            calling this function.
        """
        assert self.image is not None

        if bound_box is None:
            raise bounding_box.BoundingBoxError()
        elif len(bound_box) != 2:
            raise bounding_box.BoundingBoxError()
        elif (len(bound_box[0]) != 2) or (len(bound_box[1]) != 2):
            raise bounding_box.BoundingBoxError()
        self.feat_cam_shift = cam_shift.CamShift(self.image, bound_box[0], bound_box[1])

    def get_features(self):
        """ Gets the features of the images from the camera.
        """
        self.image = self.image_queue.get()
        windows = camera.Camera.get_windows(self.image, self.window_size, self.overlap)
        feats = np.array([])
        for r in range(0, self.window_size[1]):
            for c in range(0, self.window_size[0]):
                cur_window = self.image[windows[r][c][2]:windows[r][c][3], windows[r][c][0]:windows[r][c][1]]
                cur_window = cv2.resize(cur_window, self.feat_opt_flow.shape[::-1])
                flow = self.feat_opt_flow.extract(cur_window)
                flow_feats = optical_flow.OpticalFlow.get_features(flow)
                feats = np.vstack((feats, flow_feats)) if feats.size else flow_feats
        return np.transpose(feats)

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


def _test_parrot():
    """ Tests the parrot module
    """
    pdb.set_trace()
    parrot = Parrot()
    parrot.init_camera()
    parrot.init_feature_extract()

    while True:
        image = parrot.image_queue.get()
        features = parrot.get_features()
        with open('feat.dat', 'a') as out:
            np.savetxt(out, features)

        cv2.imshow('Image', image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

if __name__ == '__main__':
    import pdb
    _test_parrot()
