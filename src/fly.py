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
import Queue
import numpy as np

# Igor's modules.
import args
import debug
import parrot
import tracking


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
        self.verbosity = verbosity
        self.frame_rate = frame_rate
        self.remote_rate = remote_rate
        self.nav_rate = nav_rate

        self.debug_queue = Queue.Queue()
        self.error_queue = Queue.Queue()
        self.debugger = debug.Debug(verbosity, self.debug_queue, self.error_queue)

    def start(self):
        """ Starts the flying tool.
        """
        self.debug_queue.put({'MSG': 'Parrot AR 2 Flying Tool', 'PRIORITY': 1})
        if self.gui:
            self.debug_queue.put({'MSG': ':: GUI flag set.', 'PRIORITY': 1})
        self.debug_queue.put({'MSG': ':: Verbosity set to %d.' % self.verbosity, 'PRIORITY': 1})
        self.debug_queue.put({'MSG': ':: Accessing controller server at: localhost:9000.', 'PRIORITY': 1})
        self.debug_queue.put({'MSG': ':: Accessing navigation data server at: localhost:9001.', 'PRIORITY': 1})
        self.debug_queue.put({'MSG': ':: Accessing camera stream server at: tcp://192.168.1.1:5555.', 'PRIORITY': 1})
        if self.save:
            self.debug_queue.put({'MSG': ':: Saving camera stream.', 'PRIORITY': 1})

        # Create the drone object.
        self.debug_queue.put({'MSG': ':: Initializing parrot.', 'PRIORITY': 1})
        self.drone = parrot.Parrot(self.debug_queue,
                                   self.error_queue,
                                   self.address,
                                   self.learning,
                                   self.iterations,
                                   self.trajectories,
                                   self.save,
                                   self.frame_rate,
                                   self.remote_rate,
                                   self.nav_rate)

        self.debug_queue.put({'MSG': ':: Initializing remote control.', 'PRIORITY': 1})
        self.drone.init_remote()

        self.debug_queue.put({'MSG': ':: Initializing camera.', 'PRIORITY': 1})
        self.drone.init_camera()

        self.debug_queue.put({'MSG': ':: Initializing controller.', 'PRIORITY': 1})
        self.drone.init_controller()

        self.debug_queue.put({'MSG': ':: Initializing receiver.', 'PRIORITY': 1})
        self.drone.init_receiver()

        if self.drone.check_threads():
            self.debugger.debug()
            self.debug_queue.put({'MSG': ':: All threads initialized successfully.', 'PRIORITY': 1})
            self.debug_queue.put({'MSG': ':: Initializing feature extraction.', 'PRIORITY': 1})
            self.drone.init_feature_extract()
            if self.gui:
                self.debug_queue.put({'MSG': ':: Initializing GUI.', 'PRIORITY': 1})
                self.gui = self.create_gui()
                #self.gui.run()

        # Run the tool.
        self.run()

    def run(self):
        while True:
            self.debugger.debug()
            self.update_remote()
            self.update_video()

    def save_features(self, features):
        with open('feat.dat', 'a') as out:
            np.savetxt(out, features)
            out.write('\n')

    def save_image(self, image, cmd):
        directory = 'data/'
        if self.save:
            self.debug_queue.put({'MSG': 'Saving new image.', 'PRIORITY': 2})
            out = directory + 'image_%s_%s_%s.jpg' % (self.drone.dagger.i, self.drone.dagger.j, self.t)
            # image_bgr = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
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
        self.debug_queue.put({'MSG': 'Getting image from drone.', 'PRIORITY': 1})
        self.frame = self.drone.get_image()

        self.debug_queue.put({'MSG': 'Getting features from drone.', 'PRIORITY': 1})
        self.feats = self.drone.get_features()

        #self.debug_queue.put({'MSG': 'Saving image of drone.', 'Priority': 1})
        #self.save_image(self.frame, self.cmd)
        #self.save_features(self.feats)


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
    except debug.Error as e:
        # Try to land the drone.
        try:
            f.parrot.exit()
        except:
            pass
        e.print_error()
        sys.exit(1)
    except KeyboardInterrupt:
        # Try to land the drone.
        try:
            f.parrot.exit()
        except:
            pass
        print('\nClosing.')
        sys.exit(1)
    except Exception:
        pdb.set_trace()
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    import pdb
    main()
