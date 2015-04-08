#!/usr/bin/env python2.7

""" A tool that allows the user to fly the drone easily from the keyboard.
"""

import argparse
import numpy as np
import sys

import pdb

import Tkinter as tk
from PIL import ImageTk, Image

# Igor's modules.
from parrot import parrot
from parrot import tracking


class FlyToolError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg):
        self.msg = 'Error: %s' % msg

    def print_error(self):
        print(self.msg)


class FlyToolArgumentError(FlyToolError):
    def __init__(self, arg):
        self.msg = "Error: argument '%s' is invalid." % arg


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
        desc = 'A tool that allows the user to easily fly a Parrot AR Drone 2.0.'
        epil = 'Application %s version %s. Created by %s on %s for %s.' % (name, version, author, date, organ)

        # Arguments help.
        help_help = 'Show this help message and exit.'
        gui_help = 'Use this flag if you want to use the GUI.'
        stream_help = 'Use this argument if you want to record the front and bottom camera streams as mpeg. If so, pass the name of the files the streams will be saved in.'
        verb_help = 'Increase the output verbosity.'

        # Argparser.
        self.arg_parser = argparse.ArgumentParser(prog=name, description=desc, epilog=epil, add_help=False)
        optional_args = self.arg_parser.add_argument_group('Optional arguments', '')

        optional_args.add_argument('-h', '--help', action='help', help=help_help)
        optional_args.add_argument('-g', '--gui', dest='gui', action='store_true', default=False, help=gui_help)
        optional_args.add_argument('-v', '--verbosity', dest='verb', action='count', default=0, help=verb_help)
        optional_args.add_argument('-s', '--stream', type=str, dest='stream', help=stream_help, metavar='\b')

    def parse(self):
        self.args = self.arg_parser.parse_args()

        # Parse the stream argument.
        if self.args.stream is not None:
            try:
                self.args.stream = self.args.stream.split(',')
                # Make sure that the file can be accessed with correct permissions.
            except ValueError:
                raise FlyToolArgumentError(self.args.record)

        self.parse_stream()

    def parse_stream(self):
        """ Same for the stream argument.
        """
        pass


class FlyTool(object):
    """ Flying tool.

        Responsible for creating an interface that allows a user to fly the
        drone seamlessly. Also, it handles other things like printing debug
        information and saving streams.
    """
    def __init__(self, gui, verb, stream):
        self.gui = gui
        self.verb = verb
        self.stream = stream

    def start(self):
        """ Starts the flying tool.
        """
        # Print out some debug information.
        if self.verb >= 0:
            print('Parrot AR 2 Flying Tool')
        if self.verb >= 1:
            if self.gui:
                print(':: GUI flag set.')
            print(':: Verbosity set to %d.' % self.verb)
            print(':: Accessing controller server at: localhost:9000.')
            print(':: Accessing camera stream server at: tcp://192.168.1.1:5555.')
            if self.stream:
                # if self.stream[0]:
                #     print(':: Saving front camera stream to file: %s.' % self.fc_filename)
                # if self.stream[1]:
                #     print(':: Saving bottom camera stream to file: %s.' % self.br_filename)
                pass

        # Create the drone object.
        self.speed = 0.3
        self.drone = parrot.Parrot()
        try:
            self.drone.init_camera()
            self.drone.init_controller()
            self.drone.init_feature_extract()
        except Exception:
            pass

        if self.gui:
            self.gui = self.create_gui()
            self.gui.run()

    def get_features(self):
        features = self.drone.get_features()
        with open('feat.dat', 'a') as out:
            np.savetxt(out, features)
            out.write('\n')

    def get_object_to_track(self):
        """ Gets the object to track from the user.
        """
        # Get the ROI from the user.
        bound_box = tracking.bounding_box.BoundingBox(frame)
        clone = frame.copy()
        cv2.namedWindow("Grab ROI")
        cv2.setMouseCallback("Grab ROI", bound_box.click_and_bound)
        while True:
            cv2.imshow("Grab ROI", frame)
            key = cv2.waitKey()
            bound = bound_box.get_bounding_box()

            if bound_box.get_bounding_box() is not None:
                cv2.rectangle(frame, bound[0], bound[1], (0, 0, 255), 2)
                cv2.imshow("Grab ROI", frame)

            # if the 'r' key is pressed, reset the cropping region.
            if key == ord('r'):
                frame = clone.copy()

            if key == ord('n'):
                frame = self.drone.image_queue.get()
                clone = frame.copy()

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
            self.update_video()
            self.root.mainloop()
            sys.exit(0)

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
                if self.fly.verb >= 1:
                    print('Sending command to fly right at speed %0.1f.' % self.fly.speed)
                self.fly.drone.fly_right(self.fly.speed)
            elif char_pressed == 'a':
                if self.fly.verb >= 1:
                    print('Sending command to fly left at speed %0.1f.' % self.fly.speed)
                self.fly.drone.fly_left(self.fly.speed)
            elif char_pressed == 's':
                if self.fly.verb >= 1:
                    print('Sending command to fly backward at speed %0.1f.' % self.fly.speed)
                self.fly.drone.fly_backward(self.fly.speed)
            elif char_pressed == 'w':
                if self.fly.verb >= 1:
                    print('Sending command to fly forward at speed %0.1f.' % self.fly.speed)
                self.fly.drone.fly_forward(self.fly.speed)
            elif char_pressed == 'q':
                if self.fly.verb >= 1:
                    print('Sending command to turn left at speed %0.1f.' % self.fly.speed)
                self.fly.drone.turn_left(self.fly.speed)
            elif char_pressed == 'e':
                if self.fly.verb >= 1:
                    print('Sending command to turn right at speed %0.1f.' % self.fly.speed)
                self.fly.drone.turn_right(self.fly.speed)
            elif char_pressed == 'r':
                if self.fly.verb >= 1:
                    print('Sending command to fly up at speed %0.1f.' % self.fly.speed)
                self.fly.drone.fly_up(self.fly.speed)
            elif char_pressed == 'f':
                if self.fly.verb >= 1:
                    print('Sending command to fly down at speed %0.1f.' % self.fly.speed)
                self.fly.drone.fly_down(self.fly.speed)

            # Other keys.
            elif char_pressed == 't':
                if self.fly.verb >= 1:
                    print('Sending command to take off.')
                self.fly.drone.takeoff()
            elif char_pressed == 'l':
                if self.fly.verb >= 1:
                    print('Sending command to land')
                self.fly.drone.land()
            elif char_pressed == 'c':
                if self.fly.verb >= 1:
                    print('Sending command to change camera.')
                self.fly.drone.change_camera()
            elif char_pressed == ',':
                self.fly.speed += 1
                if self.fly.verb >= 1:
                    print('Changing speed to %s' + str(self.fly.speed))

        def key_release(self, event):
            """ Commands the drone to stop when the relevant keys are released.
            """
            char_released = event.keysym
            drone_stop_list = ['d', 'a', 's', 'w', 'q', 'e', 'r', 'f']
            if char_released in drone_stop_list:
                self.fly.drone.stop()

        def update_video(self):
            self.root.after(500, self.update_video)
            frame = self.fly.drone.image
            if frame is not None:
                pil_frame = Image.fromarray(frame)
                pil_frame = pil_frame.resize((400, 300), Image.ANTIALIAS)
                photo_frame = ImageTk.PhotoImage(pil_frame)
                self.cam_label.config(image=photo_frame)
                self.cam_label.image = photo_frame

                # Get the features and append to the data file.
                self.fly.get_features()


def main():
    try:
        fa = FlyToolArgs()
        fa.parse()
        f = FlyTool(fa.args.gui, fa.args.verb, fa.args.stream)
        f.start()
    except KeyboardInterrupt:
        print('\nClosing.')
        sys.exit(1)
    except FlyToolArgumentError as e:
        e.print_error()
        sys.exit(1)

if __name__ == '__main__':
    main()
