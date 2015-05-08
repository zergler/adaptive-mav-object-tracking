#!/usr/bin/env python2

""" Fly module.

    A tool that allows the user to fly the Parrot AR Drone 2.0 easily using the
    keyboard or a gamepad remote USB controller connected to the computer. The
    tool is used to train a learning algorithm by dataset aggregation (DAgger).
"""

import cv2
import json
import math
import sys
import time
import traceback
import Queue
import numpy as np
import Tkinter as tk
from PIL import ImageTk, Image

# Igor's modules.
import args
import debug
import parrot
import remote
import tracking
from tools import annotate
from feature_extraction import feature_extractor
from learning import dagger


class FlyTool(object):
    """ Flying tool.

        Responsible for creating an interface that allows a user to fly the
        drone seamlessly. Also, it handles other things like printing debug
        information and saving saves.
    """
    def __init__(self, args):
        pdb.set_trace()
        self.gui = args.gui
        self.verbosity = args.verbosity

        self.debug_queue = Queue.Queue()
        self.error_queue = Queue.Queue()
        self.debugger = debug.Debug(self.verbosity, self.debug_queue, self.error_queue)

        pdb.set_trace()
        if args.command == 'train':
            self.train(args)
        elif args.command == 'test':
            self.test(args)
        elif args.command == 'exec':
            self.execute(args)
        elif args.command == 'annotate':
            self.annotate(args)

    def train(self, args):
        """ Starts training. Make sure you have annotated the images first.
        """
        self.iterations = args.iterations
        self.learning = args.learning

        # Create the dagger object.
        self.dag = dagger.DAgger(self.learning)
        self.dag.aggregate(self.iterations)


    def execute(self, args):
        # Get the arguments for this subcommand.
        self.address = args.address
        self.learning = args.learning
        self.iteration = args.iteration
        self.trajectory = args.trajectory

        # Create the dagger object.
        self.dag = dagger.DAgger(self.learning)

        # Feature extraction parameters.
        window_size = (10, 5)
        overlap = 0.25
        cmd_history_feats = 7    # the approximate number of cmd history features
        cmd_history_length = 10  # keep a running list of the last 10 cmds
        nav_history_feats = 7    # the approximate number of nav history features
        nav_history_length = 10  # keep a running list of the last 10 nav data

        self.debug_queue.put({'MSG': 'Parrot AR 2 Flying Tool :: Training Mode', 'PRIORITY': 1})
        self.debug_queue.put({'MSG': ':: GUI flag set to %s.' % str(self.gui), 'PRIORITY': 1})
        self.debug_queue.put({'MSG': ':: Verbosity set to %d.' % self.verbosity, 'PRIORITY': 1})
        self.debug_queue.put({'MSG': ':: Accessing controller server at: %s.' % self.address[0], 'PRIORITY': 1})
        self.debug_queue.put({'MSG': ':: Accessing navigation data server at: %s.' % self.address[1], 'PRIORITY': 1})
        self.debug_queue.put({'MSG': ':: Accessing camera stream server at: tcp://192.168.1.1:5555.', 'PRIORITY': 1})

        # Create the drone object.
        self.debug_queue.put({'MSG': ':: Initializing parrot.', 'PRIORITY': 1})
        self.debugger.debug()
        self.drone = parrot.Parrot(self.debug_queue,
                                   self.error_queue,
                                   self.address,
                                   self.learning,
                                   self.iteration,
                                   self.trajectory)

        self.feature_queue = Queue.Queue(maxsize=1)
        init_image = self.drone.get_image()
        self.feature_extractor = feature_extractor.FeatureExtractor(self.feature_queue,
                                                                    init_image,
                                                                    window_size,
                                                                    overlap,
                                                                    cmd_history_feats,
                                                                    cmd_history_length,
                                                                    nav_history_feats,
                                                                    nav_history_length)

        directory = './data/%s/%s/' % (self.iteration, self.trajectory)

        # Start training.
        if self.iteration == 1:
            self.debug_queue.put({'MSG': 'Since this is the first iteration, all input will come from the expert.', 'PRIORITY': 1})
            self.debug_queue.put({'MSG': 'Waiting to take off...', 'PRIORITY': 1})
            self.debugger.debug()

        # Start when the drone takes off.
        while True:
            cmd = self.drone.get_cmd()
            self.drone.send_cmd(cmd)

            if cmd is not None:
                if cmd['T']:
                    break
        self.debug_queue.put({'MSG': 'Starting training for iteration %s, trajectory %s.', 'PRIORITY': 1})
        self.debugger.debug()

        features_filename = directory + 'features.data'
        cmd_filename = directory + 'drone_cmds.data'

        # Loop until the drone has landed.
        self.time_step = 1
        feature_flag = False
        while True:
            # Land to avoid a crash.
            emergency_cmd = self.drone.get_cmd()
            if emergency_cmd is not None:
                if emergency_cmd['L']:
                    self.drone.send_cmd(self.drone.remote.land())

            image_filename = directory + '%s.jpg' % self.time_step

            expert_cmd = self.drone.get_cmd()
            if self.iteration == 1:
                if expert_cmd is not None and not feature_flag:
                    image = self.drone.get_image()
                    navdata = self.drone.get_navdata()
                    self.feature_extractor.extract(image)
                    self.feature_extractor.update(cmd, navdata)
                    feature_flag = True
                try:
                    features = self.feature_queue.get(block=False)
                    # Save the features and command.
                    self.save_image(image, image_filename)
                    self.save_features(features, features_filename)
                    self.save_cmd(expert_cmd, cmd_filename)
                    self.time_step += 1
                    feature_flag = False
                except Queue.Empty:
                    pass
                self.drone.send_cmd(expert_cmd)
            else:
                if not feature_flag:
                    image = self.drone.get_image()
                    navdata = self.drone.get_navdata()
                    self.feature_extractor.extract(image)
                    self.feature_extractor.update(cmd, navdata)
                    feature_flag = True
                try:
                    features = self.feature_queue.get(block=False)

                    # Get the command associated with this state.
                    x = self.dag.test(features, self.iteration)
                    cmd = self.drone.default_cmd
                    cmd['X'] = cmd

                    # Save the features and command.
                    self.save_image(image, image_filename)
                    self.save_features(features, features_filename)
                    self.save_cmd(expert_cmd, cmd_filename)
                    self.time_step += 1
                    feature_flag = False
                except Queue.Empty:
                    pass
                
    def test(self, args):
        pass

    def annotate(self, args):
        self.iteration = args.iteration
        self.trajectory = args.trajectory
        self.time_step = 1
        self.video_rate = 5

        self.debug_queue.put({'MSG': 'Parrot AR 2 Flying Tool :: Annotation Mode', 'PRIORITY': 1})
        if self.gui:
            self.debug_queue.put({'MSG': ':: GUI flag set.', 'PRIORITY': 1})
        self.debug_queue.put({'MSG': ':: Verbosity set to %d.' % self.verbosity, 'PRIORITY': 1})

        # Initialize the remote module.
        self.debug_queue.put({'MSG': ':: Initializing remote control.', 'PRIORITY': 1})
        self.remote_control = remote.Remote(self.debug_queue, self.error_queue)

        # Initialize the gui.
        self.debug_queue.put({'MSG': ':: Initializing GUI.', 'PRIORITY': 1})
        self.root = tk.Tk()
        if self.root:
            self.root.resizable(0, 0)  # change this later
            self.root.wm_title("AMOT :: Annotation Tool")
            self.image_frame = tk.Frame(self.root)
            self.create_annotate_gui()

        self.debug_queue.put({'MSG': ':: Starting annotation for iteration %s, trajectory %s.' % (self.iteration, self.trajectory), 'PRIORITY': 1})
        self.debug_queue.put({'MSG': ':: To annotate, get the optimal command using the left annolog stick and press button 5 to save.', 'PRIORITY': 1})
        self.directory = './data/%s/%s/' % (args.iteration, args.trajectory)
        self.debug_queue.put({'MSG': ':: Looking in directory %s for images and commands.' % self.directory, 'PRIORITY': 1})

        # Load the commands associated with this iteration and trajectory.
        self.debug_queue.put({'MSG': ':: Loading drone commands.\n', 'PRIORITY': 1})
        cmd_filename = self.directory + 'drone_cmds.data'
        f = open(cmd_filename)
        lines = f.readlines()
        self.cmd_drone_json = lines[self.time_step - 1]

        self.debug_flag = False
        self.debugger.debug()
        self.update_annotate_gui()
        self.root.mainloop()

    def create_annotate_gui(self):
        """ Creates the gui for the annotation tool.
        """
        # Create the layout of the frames.
        self.image_frame.pack()

        # Test images for frames.
        test_image = Image.open('../samples/test_image.jpg')
        test_photo = ImageTk.PhotoImage(test_image)
        self.image_label = tk.Label(self.image_frame, image=test_photo)
        self.image_label.image = test_photo

        # self.world_label.bind('<Configure>', self.resize)
        self.image_label.pack()

    def update_annotate_gui(self):
        """ Updates the annotation gui image with the new image.
        """
        self.root.after(int(math.floor(1000.0/self.video_rate)), self.update_annotate_gui)

        # Load the image.
        image = None
        image_filename = self.directory + '%s.jpg' % self.time_step
        image = cv2.imread(image_filename)

        if image is None:
            self.debug_queue.put({'MSG': 'No more time-steps. Exiting...', 'PRIORITY': 1})
            self.debugger.debug()
            self.root.quit()
            return

        if not self.debug_flag:
            self.debug_queue.put({'MSG': 'Starting annotation for time-step %s.' % self.time_step, 'PRIORITY': 1})
            self.debugger.debug()
            self.debug_flag = True

        try:
            cmd_expert = self.remote_control.get_input()
            cmd_drone = json.loads(self.cmd_drone_json)
            annotated_image = annotate.annotate(image, cmd_drone, cmd_expert)

            # Display the image.
            if annotated_image is not None:
                pil_frame = Image.fromarray(annotated_image)
                pil_frame = pil_frame.resize((400, 300), Image.ANTIALIAS)
                photo_frame = ImageTk.PhotoImage(pil_frame)
                self.image_label.config(image=photo_frame)
                self.image_label.image = photo_frame

            # If the user wants to save the current expert command, save it.
            if cmd_expert['A']:
                filename = self.directory + 'expert_cmds.data'
                self.save_cmd(cmd_expert, filename)
                self.time_step += 1
                self.debug_flag = False

        except Queue.Empty:
            pass

    def save_features(self, features, filename):
        self.debug_queue.put({'MSG': "Saving features for time-step %s to file: %s." % (self.time_step, filename), 'PRIORITY': 1})
        self.debugger.debug()
        with open(filename, 'a') as out:
            line = np.hstack(([[self.time_step]], features))
            np.savetxt(out, line)

    def save_image(self, image, filename):
        self.debug_queue.put({'MSG': "Saving image for time-step %s to file: %s." % (self.time_step, filename), 'PRIORITY': 1})
        self.debugger.debug()
        # image_bgr = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(filename, image)

    def save_cmd(self, cmd, filename):
        self.debug_queue.put({'MSG': "Saving command for time-step %s to file: %s." % (self.time_step, filename), 'PRIORITY': 1})
        self.debugger.debug()
        with open(filename, 'a') as f:
            cmd_json = json.dumps(cmd) + '\n'
            f.write(cmd_json)

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


def main():
    try:
        fa = args.FlyArgs()
        fa.parse()
        f = FlyTool(fa.args)
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
