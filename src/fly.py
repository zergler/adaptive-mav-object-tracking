#!/usr/bin/env python2

""" Fly module.

    A tool that allows the user to fly the Parrot AR Drone 2.0 easily using the
    keyboard or a gamepad remote USB controller connected to the computer. The
    tool is used to train a learning algorithm by dataset aggregation (DAgger).
"""

import cv2
import math
import sys
import traceback
import numpy as np

# Igor's modules.
import args
import debug
import parrot
import tracking


class FlyError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg='', warning=False):
        default_header = 'Error: fly:'
        default_error = '%s an exception occured.' % default_header
        self.msg = default_error if msg == '' else '%s %s.' % (default_header, msg)
        self.warning = warning

    def print_error(self):
        print(self.msg)


class FlyTool(object):
    """ Flying tool.

        Responsible for creating an interface that allows a user to fly the
        drone seamlessly. Also, it handles other things like printing debug
        information and saving saves.
    """
    def __init__(self, address, learning, iterations, trajectories, gui, save, verbosity, frame_rate, remote_rate, nav_rate):
        self.address = address
        self.learning = learning
        self.iterations = iterations
        self.trajectories = trajectories
        self.gui = gui
        self.save = save
        self.frame_rate = frame_rate
        self.remote_rate = remote_rate
        self.nav_rate = nav_rate

        self.debug = debug.Debug(verbosity)
        pdb.set_trace()

    def start(self):
        """ Starts the flying tool.
        """
        self.debug.print_debug('Parrot AR 2 Flying Tool')
        if self.gui:
            self.debug.print_debug(':: GUI flag set.')
        self.debug.debug(':: Verbosity set to %d.' % self.verbosity)
        self.debug.debug(':: Accessing controller server at: localhost:9000.')
        self.debug.debug(':: Accessing navigation data server at: localhost:9001.')
        self.debug.debug(':: Accessing camera stream server at: tcp://192.168.1.1:5555.')
        if self.save:
            self.debug.debug(':: Saving camera stream.')

        # Create the drone object.
        self.speed = 0.3
        self.drone = parrot.Parrot(self.address,
                                   self.learning,
                                   self.iterations,
                                   self.trajectories,
                                   self.save,
                                   self.frame_rate,
                                   self.remote_rate,
                                   self.nav_rate)

        remote_init = self.drone.init_remote()
        camera_init = self.drone.init_camera()
        controller_init = self.drone.init_controller()
        receiver_init = self.drone.init_receiver()
        self.drone.init_feature_extract()

        # Only start the gui if all of the threads have been successfully
        # initialized and the user wants to use it.
        if remote_init and camera_init and controller_init and receiver_init:
            if self.gui:
                self.gui = self.create_gui()
                self.gui.run()

    def save_features(self, features):
        with open('feat.dat', 'a') as out:
            np.savetxt(out, features)
            out.write('\n')

    def save_image(self, image, cmd):
        directory = 'data/'
        if self.save:
            out = directory + 'image_%s_%s_%s.jpg' % (self.dagger.i, self.dagger.j, self.t)
            image_bgr = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(out, image_bgr)
            self.t += 1

    def get_object_to_track(self):
        """ Gets the object to track from the user.
        """
        # Get the ROI from the user.
        bound_box = tracking.bounding_box.BoundingBox(self.frame)
        clone = self.frame.copy()
        cv2.namedWindow("Grab ROI")
        cv2.setMouseCallback("Grab ROI", bound_box.click_and_bound)
        while True:
            cv2.imshow("Grab ROI", self.frame)
            key = cv2.waitKey()
            bound = bound_box.get_bounding_box()

            if bound_box.get_bounding_box() is not None:
                cv2.rectangle(self.frame, bound[0], bound[1], (0, 0, 255), 2)
                cv2.imshow("Grab ROI", self.frame)

            # if the 'r' key is pressed, reset the cropping region.
            if key == ord('r'):
                self.frame = clone.copy()

            if key == ord('n'):
                self.frame = self.drone.get_image()
                clone = self.frame.copy()

            if key == ord('q'):
                break

    def create_gui(self):
        """ Builds the OpenCV gui.
        """
        pass

    def update_remote(self):
        # int(math.floor(1000.0/self.remote_rate))

        # Execute commands from the drone.
        self.cmd = self.drone.get_cmd()
        self.drone.send_cmd(self.cmd)

    def update_video(self):
        # int(math.floor(1000.0/self.frame_rate))
        # Save the images and features if the user has asked to.
        pdb.set_trace()
        self.frame = self.drone.get_image()
        self.feats = self.drone.get_features()
        self.save_image(self.frame, self.cmd)
        self.save_features(self.feats)

        # Display the image if the user has asked to.


def main():
    try:
        fa = args.FlyArgs()
        fa.parse()
        f = FlyTool(fa.args.address,
                    fa.args.learning,
                    fa.args.iterations,
                    fa.args.trajectories,
                    fa.args.gui,
                    fa.args.save,
                    fa.args.verbosity,
                    fa.args.frame_rate,
                    fa.args.remote_rate,
                    fa.args.nav_rate)
        f.start()
    except args.FlyArgsError as e:
        e.print_error()
    except FlyError as e:
        f.parrot.exit()
        e.print_error()
        sys.exit(1)
    except KeyboardInterrupt:
        f.parrot.exit()
        print('\nClosing.')
        sys.exit(1)
    except Exception:
        pdb.set_trace()
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    import pdb
    main()
