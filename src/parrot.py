
""" Parrot module.

    Allows access to the drone's front and bottom cameras, the ability to
    send commands, and the ability to read the drone's navigation data.
"""

import cv2
import json
import Queue
import numpy as np

# Local modules.
import remote
import camera
import controller
import debug
import receiver

# Tracking modules.
from tracking import bounding_box
from tracking import cam_shift


class Parrot(object):
    """ Encapsulates the AR Parrot Drone 2.0.

        Allows access to the drone's front and bottom cameras, the ability to
        send commands, and the ability to read the drone's navigation data.
    """
    def __init__(self, debug_queue, error_queue, address, learning, iteration, trajectory):
        (self.controller_address, self.receiver_address) = address
        self.debug_queue = debug_queue
        self.error_queue = error_queue

        self.learning = learning
        self.iterations = iteration
        self.trajectories = trajectory

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
        self.drone_address = '192.168.1.1'
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

        
        # The method of tracking we are going to use.
        self.tracking = None

        # Initialize all modules.
        self.remote = remote.Remote(self.debug_queue, self.error_queue)
        self.controller = controller.Controller(self.debug_queue, self.error_queue)
        self.receiver = receiver.Receiver(self.debug_queue, self.error_queue)

        camera_address = 'tcp://' + self.drone_address + ':' + str(self.ports['VIDEO'])
        self.image_queue = Queue.Queue(maxsize=1)
        self.camera = camera.Camera(self.debug_queue, self.error_queue, camera_address, self.image_queue)
        self.camera.daemon = True
        self.camera.start()

    def get_navdata(self):
        navdata = self.receiver.get_navdata()
        return navdata

    def get_image(self):
        image = self.image_queue.get(block=True)
        return image

    def get_cmd(self):
        cmd = self.remote.get_input()
        return cmd

    def send_cmd(self, cmd):
        cmd_json = json.dumps(cmd)
        self.controller.send_cmd(cmd_json)

    def exit(self):
        """ Lands the drone, closes all cv windows and exits.
        """
        self.land()
        cv2.destroyAllWindows()


def _test_parrot():
    """ Tests the parrot module
    """
    pdb.set_trace()

    nav_rate = 1
    save = True
    iterations = 3
    trajectories = 2
    parrot = Parrot(save, iterations, trajectories)
    parrot.init_camera()
    parrot.init_receiver(nav_rate)
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
