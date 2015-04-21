#!/usr/bin/env python2.7

""" Fly module.

    A tool that allows the user to fly the Parrot AR Drone 2.0 easily using the
    keyboard or a gamepad remote USB controller connected to the computer. The
    tool is used to train a learning algorithm by dataset aggregation (DAgger).
"""

import argparse
import cv2
import math
import numpy as np
import sys
import traceback

import Tkinter as tk
from PIL import ImageTk, Image

# Igor's modules.
import parrot
import tracking


class FlyError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg='', warning=False):
        default_header = 'Error: fly'
        default_error = '%s: an exception occured.' % default_header
        self.msg = default_error if msg == '' else '%s: %s.' % (default_header, msg)
        self.warning = warning

    def print_error(self):
        print(self.msg)


class FlyToolArgs(object):
    """ Argument parser for flying tool.
    """
    def __init__(self):
        # Basic info.
        version = 1.0
        name = 'fly'
        date = '02/21/15'
        author = 'Igor Janjic'
        organ = 'Graduate Research at Virginia Tech'
        desc = 'A tool that allows the user to fly the Parrot AR Drone 2.0 easily using the keyboard or a gamepad remote USB controller connected to the computer. The tool is used to train a learning algorithm by dataset aggregation (DAgger).'
        epil = 'Application %s version %s. Created by %s on %s for %s.' % (name, version, author, date, organ)

        # Arguments help.
        address_help = 'The addresses of the controller server and receiver server.'
        learning_help = "The type of learning algorithm to use. Use 'tkhonov' for Tikhonov regression or 'ordinary_least_squares' for ordinary least squares linear regression."
        iterations_help = 'The number of iterations of learning to do.'
        trajectories_help = 'The number of trajectories to include per iteration of learning.'
        frame_rate_help = 'The number of times per second to query the camera for images. Default is 5 frames/s.'
        remote_rate_help = 'The number of times per second to query the remote for commands. Default is 2 queries/s.'
        nav_rate_help = 'The number of times per second to query the receiver for navigation data. Default is 1 queries/s.'

        help_help = 'Show this help message and exit.'
        gui_help = 'Use this flag if you want to use the GUI. Default is to not launch the GUI.'
        save_help = 'Use this argument if you want to record the camera as mpeg. Default is to save the video for the current iteration and trajectory with the filename samples/video_i_j.mpeg, where i is the current iteration and j is the current trajectory.'
        verbosity_help = 'Increase the output verbosity.'

        # Argparser.
        self.arg_parser = argparse.ArgumentParser(prog=name, description=desc, epilog=epil, add_help=False)
        required_args = self.arg_parser.add_argument_group('Required arguments', '')
        optional_args = self.arg_parser.add_argument_group('Optional arguments', '')

        required_args.add_argument('-a', '--address', required=True, type=str, nargs=2, help=address_help)
        required_args.add_argument('-l', '--learning', required=True, type=str, help=learning_help)
        required_args.add_argument('-i', '--iterations', required=True, type=int, help=iterations_help)
        required_args.add_argument('-t', '--trajectories', required=True, type=int, help=trajectories_help)

        optional_args.add_argument('-h', '--help', action='help', help=help_help)
        optional_args.add_argument('-g', '--gui', action='store_true', default=False, help=gui_help)
        optional_args.add_argument('-v', '--verbosity', action='count', default=0, help=verbosity_help)
        optional_args.add_argument('-s', '--save', action='store_true', default=True, help=save_help)

        optional_args.add_argument('-f', '--frame-rate', default=5, type=int, help=frame_rate_help)
        optional_args.add_argument('-r', '--remote-rate', default=2, type=int, help=remote_rate_help)
        optional_args.add_argument('-n', '--nav-rate', default=1, type=int, help=nav_rate_help)

    def parse(self):
        self.args = self.arg_parser.parse_args()

        # Parse the address argument.

        # Parse the save argument.
        if self.args.save is not None:
            try:
                # Make sure that the file can be accessed with correct permissions.
                pass
            except ValueError:
                raise FlyError(self.args.record)


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
        pdb.set_trace()

    def start(self):
        """ Starts the flying tool.
        """
        # Print out some debug information.
        if self.verbosity >= 0:
            print('Parrot AR 2 Flying Tool')
        if self.verbosity >= 1:
            if self.gui:
                print(':: GUI flag set.')
            print(':: Verbosity set to %d.' % self.verbosity)
            print(':: Accessing controller server at: localhost:9000.')
            print(':: Accessing navigation data server at: localhost:9001.')
            print(':: Accessing camera stream server at: tcp://192.168.1.1:5555.')
            if self.save:
                if self.save:
                    print(':: Saving camera stream.')

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
        """ Factory method that builds the GUI and passes the fly object to it.
        """
        return FlyTool.FlyToolGUI(self)

    class FlyToolGUI(object):
        """ GUI for flying tool.
        """
        def __init__(self, fly):
            self.fly = fly
            self.root = tk.Tk()
            if self.root:
                self.root.resizable(0, 0)  # change this later
                self.root.wm_title("Parrot AR 2 Flying Tool")
                self.cam_frame = tk.Frame(self.root)
                self.create_gui()

        def run(self):
            self.update_remote()
            self.update_video()
            self.root.mainloop()
            self.fly.drone.exit()

        def create_gui(self):
            """ Creates the gui.
            """
            # Bind the keyboard keys to command the drone.
            self.cam_frame.bind_all('<Key>', self.key_press)
            self.cam_frame.bind_all('<KeyRelease>', self.key_release)

            # Create the layout of the frames.
            self.cam_frame.pack()

            # Test images for frames.
            test_image = Image.open('../samples/test_image.jpg')
            test_photo = ImageTk.PhotoImage(test_image)
            self.cam_label = tk.Label(self.cam_frame, image=test_photo)
            self.cam_label.image = test_photo

            # self.world_label.bind('<Configure>', self.resize)
            self.cam_label.pack()

        def key_press(self, event):
            """ Commands the drone to fly using key presses.
            """
            char_pressed = event.keysym

            # Flying keys (persistent).
            if char_pressed == 'd':
                if self.fly.verbosity >= 1:
                    print('Sending command to fly right at speed %0.1f.' % self.fly.speed)
                self.fly.drone.fly_right(self.fly.speed)
            elif char_pressed == 'a':
                if self.fly.verbosity >= 1:
                    print('Sending command to fly left at speed %0.1f.' % self.fly.speed)
                self.fly.drone.fly_left(self.fly.speed)
            elif char_pressed == 's':
                if self.fly.verbosity >= 1:
                    print('Sending command to fly backward at speed %0.1f.' % self.fly.speed)
                self.fly.drone.fly_backward(self.fly.speed)
            elif char_pressed == 'w':
                if self.fly.verbosity >= 1:
                    print('Sending command to fly forward at speed %0.1f.' % self.fly.speed)
                self.fly.drone.fly_forward(self.fly.speed)
            elif char_pressed == 'q':
                if self.fly.verbosity >= 1:
                    print('Sending command to turn left at speed %0.1f.' % self.fly.speed)
                self.fly.drone.turn_left(self.fly.speed)
            elif char_pressed == 'e':
                if self.fly.verbosity >= 1:
                    print('Sending command to turn right at speed %0.1f.' % self.fly.speed)
                self.fly.drone.turn_right(self.fly.speed)
            elif char_pressed == 'r':
                if self.fly.verbosity >= 1:
                    print('Sending command to fly up at speed %0.1f.' % self.fly.speed)
                self.fly.drone.fly_up(self.fly.speed)
            elif char_pressed == 'f':
                if self.fly.verbosity >= 1:
                    print('Sending command to fly down at speed %0.1f.' % self.fly.speed)
                self.fly.drone.fly_down(self.fly.speed)

            # Other keys.
            elif char_pressed == 't':
                if self.fly.verbosity >= 1:
                    print('Sending command to take off.')
                self.fly.drone.takeoff()
            elif char_pressed == 'l':
                if self.fly.verbosity >= 1:
                    print('Sending command to land')
                self.fly.drone.land()
            elif char_pressed == 'c':
                if self.fly.verbosity >= 1:
                    print('Sending command to change camera.')
                if self.fly.drone.active_camera == 'FRONT':
                    self.fly.drone.change_camera('BOTTOM')
                else:
                    self.fly.drone.change_camera('FRONT')
            elif char_pressed == ',':
                self.fly.speed += 1
                if self.fly.verbosity >= 1:
                    print('Changing speed to %s' + str(self.fly.speed))

        def key_release(self, event):
            """ Commands the drone to stop when the relevant keys are released.
            """
            char_released = event.keysym
            drone_stop_list = ['d', 'a', 's', 'w', 'q', 'e', 'r', 'f']
            if char_released in drone_stop_list:
                self.fly.drone.stop()

        def update_remote(self):
            # Update this function every once in a while.
            self.root.after(int(math.floor(1000.0/self.fly.remote_rate)), self.update_remote)

            # Execute commands from the drone.
            self.cmd = self.fly.drone.get_cmd()
            self.fly.drone.send_cmd(self.cmd)

        def update_video(self):
            # Update this function every once in a while.
            #self.root.after(int(math.floor(1000.0/self.fly.frame_rate)), self.update_video)

            # Save the images and features if the user has asked to.
            pdb.set_trace()
            self.frame = self.fly.drone.get_image()
            self.feats = self.fly.drone.get_features()
            self.save_image(self.frame, self.cmd)
            self.save_features(self.feats)

            # Display the image.
            if self.frame is not None:
                pil_frame = Image.fromarray(self.frame)
                pil_frame = pil_frame.resize((400, 300), Image.ANTIALIAS)
                photo_frame = ImageTk.PhotoImage(pil_frame)
                self.cam_label.config(image=photo_frame)
                self.cam_label.image = photo_frame


def main():
    try:
        fa = FlyToolArgs()
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
