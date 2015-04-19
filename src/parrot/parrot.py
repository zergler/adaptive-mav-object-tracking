#!/usr/bin/env python2

import cv2
import json
import Queue
import numpy as np


# Local modules.
import remote
import camera
import controller
import receiver

# Feature modules.
from feature_extraction import hough_transform
from feature_extraction import optical_flow
from feature_extraction import laws_mask
from feature_extraction import history

# Tracking modules.
from tracking import bounding_box
from tracking import cam_shift

# Learning modules.
from learning import dagger


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
        send commands, and the ability to read the drone's navigation data.
    """
    def __init__(self, fps, save, iterations, trajectories, regressor='tikhonov'):
        # The default command that is sent to the drone.
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

        # The drone's address and ports.
        self.address = '192.168.1.1'
        self.ports = {
            'NAVDATA': 5554,
            'VIDEO':   5555,
            'CMD':     5556
        }

        # The drone's cameras.
        self.cameras = {
            'FRONT':  0,
            'BOTTOM': 3,
            'CUSTOM': 4
        }
        self.active_camera = self.cameras['FRONT']

        # Where we save the video.
        self.save = save
        self.video = None

        # Feature extraction parameters.
        self.window_size = (15, 7)
        self.overlap = 0.5
        self.fps = fps  # the number of features per second to process
        self.cmd_history_length = 10  # keep a running list of the last 10 cmds

        # Where we get our features.
        self.image = None
        self.navdata = None

        # The method of tracking we are going to use.
        self.tracking = None

        # The method of learning we are going to use.
        self.possible_regressors = ['tikhonov', 'linear_least_squares']
        self.dagger = dagger.DAgger(regressor, iterations, trajectories)

    def init_remote(self):
        """ Initializes the remote control.
        """
        self.remote_queue = Queue.Queue(maxsize=1)
        self.remote_bucket = Queue.Queue()
        self.remote = remote.Remote(self.remote_queue, self.remote_bucket)
        self.remote.daemon = True
        self.remote.start()

        # Grab the initial remote data so we know it is initialized.
        self.get_cmd()

    def init_camera(self):
        """ Initializes the camera thread.
        """
        camera_address = 'tcp://' + self.address + ':' + str(self.ports['VIDEO'])
        self.image_queue = Queue.Queue(maxsize=1)
        self.image_bucket = Queue.Queue()
        self.camera = camera.Camera(camera_address, self.image_queue, self.image_bucket)
        self.camera.daemon = True
        self.camera.start()

        # Grab the initial image so we know the camera is initialized.
        self.get_image()

        # Start saving the video if we need to.
        (width, height, _) = self.image.shape
        video_name = '../src/data/video_%s_%s.avi' % (self.dagger.i, self.dagger.j)
        self.video = cv2.VideoWriter(video_name, -1, 1, (width, height))

    def init_controller(self):
        """ Initializes the controller thread.
        """
        self.cmd_queue = Queue.Queue(maxsize=1)
        self.cmd_bucket = Queue.Queue()
        self.controller = controller.Controller(self.cmd_queue, self.cmd_bucket)
        self.controller.daemon = True
        self.controller.start()

    def init_receiver(self):
        """ Initializes the receiver thread.
        """
        self.nav_queue = Queue.Queue(maxsize=1)
        self.nav_bucket = Queue.Queue()
        self.receiver = receiver.Receiver(self.nav_queue, self.nav_bucket)
        self.receiver.daemon = True
        self.receiver.start()

        # Grab the initial nav data so we know the receiver is initialized.
        self.get_navdata()

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
        self.tracking = cam_shift.CamShift(self.image, bound_box[0], bound_box[1])

    def init_feature_extract(self):
        """ Initializes feature extraction. Make sure the camera and receiver
            are initialized before calling this function.
        """
        assert self.image is not None
        assert self.navdata is not None

        # Grab an example window from the initial image to feed the optical flow
        # feature extractor (use a non border window).
        windows = camera.Camera.get_windows(self.image, self.window_size, self.overlap)
        small_image = self.image[windows[1][1][2]:windows[1][1][3], windows[1][1][0]:windows[1][1][1]]

        # Initialize each feature extractor.
        self.extractor_opt_flow = optical_flow.OpticalFlow(small_image)
        self.extractor_hough_trans = hough_transform.HoughTransform()
        self.extractor_laws_mask = laws_mask.LawsMask()
        # self.extractor_cmd_history = history.CmdHistory(self.cmd_history_length, self.fps)
        self.extractor_nav_history = history.NavHistory()

    def check_remote(self):
        """ Checks the remote thread to see if it's okay.
        """
        # First make sure it is still running.
        okay = self.remote.isAlive()

        # Grab any exceptions it may have generated.
        try:
            error = self.remote_bucket.get(block=False)
            raise error
        except Queue.Empty:
            pass
        except remote.RemoteError as e:
            # If the error is a warning, print the warning, otherwise exit.
            if e.warning:
                print(e.msg)
            else:
                raise
        return okay

    def check_camera(self):
        """ Checks the camera thread to see if it's okay.
        """
        # First make sure it is still running.
        okay = self.camera.isAlive()

        # Grab any exceptions it may have generated.
        try:
            error = self.camera_bucket.get(block=False)
            raise error
        except Queue.Empty:
            pass
        except remote.RemoteError as e:
            # If the error is a warning, print the warning, otherwise exit.
            if e.warning:
                print(e.msg)
            else:
                raise
        return okay

    def check_controller(self):
        """ Checks the controller thread to see if it's okay.
        """
        # First make sure it is still running.
        okay = self.controller.isAlive()

        # Grab any exceptions it may have generated.
        try:
            error = self.controller_bucket.get(block=False)
            raise error
        except Queue.Empty:
            pass
        except controller.ControllerError as e:
            # If the error is a warning, print the warning, otherwise exit.
            if e.warning:
                print(e.msg)
            else:
                raise
        return okay

    def check_receiver(self):
        """ Checks the receiver thread to see if it's okay.
        """
        # First make sure it is still running.
        okay = self.receiver.isAlive()

        # Grab any exceptions it may have generated.
        try:
            error = self.nav_bucket.get(block=False)
            raise error
        except Queue.Empty:
            pass
        except remote.ReceiverError as e:
            # If the error is a warning, print the warning, otherwise exit.
            if e.warning:
                print(e.msg)
            else:
                raise
        return okay

    def get_visual_features(self):
        """ Gets the features of the images from the camera. Make sure the
            camera and feature extraction are initialized before calling this
            function. Allow the calling module to set the rate at which images
            are received from the camera thread.
        """
        assert self.image is not None
        assert self.extractor_opt_flow is not None
        assert self.extractor_hough_trans is not None
        assert self.extractor_laws_mask is not None

        # Get the windows from the current image.
        windows = camera.Camera.get_windows(self.image, self.window_size, self.overlap)

        # Arrays that will contain the different features.
        feats_all = np.array([])
        feats_flow = np.arrary([])
        feats_hough = np.arry([])
        feats_laws = np.array([])

        # Iterate through the windows, computing features for each.
        for r in range(0, self.window_size[1]):
            for c in range(0, self.window_size[0]):
                # Get the current window of the image for which the features
                # will be extracted from.
                cur_window = self.image[windows[r][c][2]:windows[r][c][3], windows[r][c][0]:windows[r][c][1]]

                # If the current window is a border window, it may have a
                # smaller size, so reshape it.
                cur_window = cv2.resize(cur_window, self.extractor_opt_flow.shape[::-1])

                # Get the optical flow features from the current window.
                flow = self.extractor_opt_flow.extract(cur_window)
                feats_cur = optical_flow.OpticalFlow.get_features(flow)
                feats_flow = np.vstack((feats_flow, feats_cur)) if feats_flow.size else feats_cur

                # Get the Hough transform features from the current window.
                lines = self.extractor_hough_trans.extract(cur_window)
                feats_cur = self.extractor_hough_trans.get_features(lines)
                feats_hough = np.vstack((feats_hough, feats_cur)) if feats_hough.size else feats_cur

                # Get the Law's texture mask features from the current window.
                feats_cur = self.extractor_laws_mask.extract(cur_window)
                feats_laws = np.vstack((feats_laws, feats_cur)) if feats_laws.size else feats_cur

        # Vertically stack all of the different features.
        feats_all = np.vstack((feats_all, feats_flow)) if feats_all.size else feats_flow
        feats_all = np.vstack((feats_all, feats_hough)) if feats_all.size else feats_hough
        feats_all = np.vstack((feats_all, feats_laws)) if feats_all.size else feats_laws

        # Transpose and return.
        return np.transpose(feats_all)

    def get_nav_features(self):
        """ Gets the features from the navigation data of the drone. Make sure
            the receiver is initialized before calling this function. Allow the
            calling module to set the rate at which navigation data is received
            from the receiver thread.
        """
        assert self.navdata is not None
        # assert self.extractor_cmd_history is not None
        # assert self.extractor_nav_history is not None

        # Get the command history features.
        feats_cmd_history = self.extractor_cmd_history.extract()
        feats_nav_history = self.extractor_nav_history.extract()
        feats_all = np.vstack((feats_cmd_history, feats_nav_history))
        return feats_all

    def get_features(self):
        visual_features = self.get_visual_features()
        nav_features = self.get_nav_features()
        feats = np.hstack((visual_features, nav_features))
        return feats

    def get_navdata(self):
        """ Receives the most recent navigation data from the drone. Calling
            module should call this function in a loop to get navigation data
            continuously. Make sure the receiver is initialized.
        """
        try:
            self.navdata = self.nav_queue.get(block=False)
        except Queue.Empty:
            pass
        return self.navdata

    def get_image(self):
        """ Receives the most recent image from the drone. Calling module should
            call this function in a loop to get images continuously. Make sure
            the camera is initialized.
        """
        try:
            self.image = self.image_queue.get(block=False)
        except Queue.Empty:
            pass

        # Save the video if we need to.
        if self.video is not None:
            self.video.write(self.image)

        return self.image

    def get_cmd(self):
        """ Receives the most recent command from the remote. Calling module
            should call this function in a loop to get the the commands
            continuously. Make sure the remote is initialized.
        """
        self.cmd = self.default_cmd.copy()
        try:
            self.cmd = self.remote_queue.get(block=False)
        except Queue.Empty:
            pass
        return self.cmd

    def send_cmd(self, cmd):
        """ Before exiting, safely lands the drone and closes all processes.
            Make sure the controller is initialized.
        """
        cmd_json = json.dumps(cmd)
        try:
            self.cmd_queue.put(cmd_json, block=False)
        except Queue.Full:
            pass

        # Add the send command to the command history feature extractor.
        # self.extractor_cmd_history.update(cmd)

    def exit(self):
        """ Lands the drone, closes all cv windows and exits.
        """
        self.land()
        cv2.destroyAllWindows()
        self.video.release()

    def land(self):
        cmd = self.default_cmd.copy()
        cmd['L'] = True
        self.send_cmd(cmd)

    def takeoff(self):
        cmd = self.default_cmd.copy()
        cmd['T'] = True
        self.send_cmd(cmd)

    def stop(self):
        cmd = self.default_cmd.copy()
        cmd['S'] = True
        self.send_cmd(cmd)

    def turn_left(self, speed):
        cmd = self.default_cmd.copy()
        cmd['R'] = -speed
        self.send_cmd(cmd)

    def turn_right(self, speed):
        cmd = self.default_cmd.copy()
        cmd['R'] = speed
        self.send_cmd(cmd)

    def fly_up(self, speed):
        cmd = self.default_cmd.copy()
        cmd['Z'] = speed
        self.send_cmd(cmd)

    def fly_down(self, speed):
        cmd = self.default_cmd.copy()
        cmd['Z'] = -speed
        self.send_cmd(cmd)

    def fly_forward(self, speed):
        cmd = self.default_cmd.copy()
        cmd['Y'] = speed
        self.send_cmd()

    def fly_backward(self, speed):
        cmd = self.default_cmd.copy()
        cmd['Y'] = -speed
        self.send_cmd(cmd)

    def fly_left(self, speed):
        cmd = self.default_cmd.copy()
        cmd['X'] = -speed
        self.send_cmd(cmd)

    def fly_right(self, speed):
        cmd = self.default_cmd.copy()
        cmd['X'] = speed
        self.send_cmd(cmd)

    def change_camera(self, camera):
        cmd = self.fly.default_cmd.copy()
        cmd['C'] = camera
        self.send_cmd(cmd)


def _test_parrot():
    """ Tests the parrot module
    """
    pdb.set_trace()

    fps = 2
    save = True
    iterations = 3
    trajectories = 2
    parrot = Parrot(fps, save, iterations, trajectories)
    parrot.init_camera()
    parrot.init_receiver()
    parrot.init_feature_extract()

    while True:
        image = parrot.get_image()
        parrot.get_navdata()

        visual_features = parrot.get_visual_features()
        # nav_features = parrot.get_nav_features()
        with open('feat.dat', 'a') as out:
            np.savetxt(out, visual_features)

        cv2.imshow('Image', image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

if __name__ == '__main__':
    import pdb
    _test_parrot()
