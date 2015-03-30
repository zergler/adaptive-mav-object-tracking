#!/usr/bin/env python2.7

""" A tool that allows the user to fly the drone easily from a gui application.
"""

import argparse
import errno
import json
import sys
import socket
import threading
import urllib2

import cv2
import numpy as np
import Tkinter as tk
from PIL import ImageTk, Image

# Igor's modules.
import feature_extraction.optical_flow as opt_flow

DEBUG = 0
try:
    import pdb
except ImportError:
    DEBUG = 0


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


class ConnectionError(Error):
    def __init__(self):
        self.msg = 'Error: connection to drone refused.'


class CameraError(Error):
    def __init__(self):
        self.msg = 'Error: cannot get image stream from drone.'


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
        url_help = 'URL of the controller server and camera server seperated by a comma.'
        port_help = 'Port of the controller server and camera server seperated by a comma.'

        # Argparser.
        self.arg_parser = argparse.ArgumentParser(prog=name, description=desc, epilog=epil, add_help=False)
        required_args = self.arg_parser.add_argument_group('Required arguments', '')
        optional_args = self.arg_parser.add_argument_group('Optional arguments', '')

        optional_args.add_argument('-h', '--help', action='help', help=help_help)
        optional_args.add_argument('-g', '--gui', dest='gui', action='store_true', default=False, help=gui_help)
        optional_args.add_argument('-v', '--verbosity', dest='verb', action='count', default=0, help=verb_help)
        optional_args.add_argument('-s', '--stream', type=str, dest='stream', help=stream_help, metavar='\b')
        required_args.add_argument('-u', '--url', type=str, dest='url', required=True, help=url_help, metavar='\b')
        required_args.add_argument('-p', '--port', type=str, dest='port', required=True, help=port_help, metavar='\b')

    def parse(self):
        self.args = self.arg_parser.parse_args()

        # Parse the url and port arguments.
        try:
            self.args.url = self.args.url.split(',')
            self.args.port = self.args.port.split(',')
        except ValueError:
            raise ArgumentError(self.args.url)

        # Parse the record argument.
        if self.args.stream is not None:
            try:
                self.args.stream = self.args.stream.split(',')
                # Make sure that the file can be accessed with correct permissions.
            except ValueError:
                raise ArgumentError(self.args.record)

        self.parse_port()
        self.parse_url()
        self.parse_stream()

    def parse_port(self):
        """ Make sure the port argument isn't junk.
        """
        if not (len(self.args.port[0]) == 4 and self.args.port[0].isdigit()):
            raise ArgumentError(self.args.port[0])
        if not (len(self.args.port[1]) == 4 and self.args.port[1].isdigit()):
            raise ArgumentError(self.args.port[1])

    def parse_url(self):
        """ Same for the url argument.
        """
        if not (self.args.url[0] == 'localhost' or self.args.url[1] == 'localhost'):
            if not len(self.args.url[0]) > 7:
                raise ArgumentError(self.args.port[0])
            if not len(self.args.url[1]) > 7:
                raise ArgumentError(self.args.port[1])
            if not self.args.url[0][:7] == 'http://':
                raise ArgumentError(self.args.port[0])
            if not self.args.url[1][:7] == 'http://':
                raise ArgumentError(self.args.port[1])

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
    def __init__(self, gui, verb, url, port, stream):
        self.gui = gui
        self.verb = verb
        self.url = url
        self.port = port
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
            print(':: Accessing controller server at: %s:%s.' % (self.url[0], self.port[0]))
            print(':: Accessing camera stream server at port: %s:%s.' % (self.url[1], self.port[1]))
            if self.stream:
                # if self.stream[0]:
                #     print(':: Saving front camera stream to file: %s.' % self.fc_filename)
                # if self.stream[1]:
                #     print(':: Saving bottom camera stream to file: %s.' % self.br_filename)
                pass

        # Create the drone object.
        self.drone = Drone(self.url[0], self.port[0], self.url[1], self.port[1])

        if self.gui:
            self.gui = self.create_gui()
            self.gui.run()

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
                self.menu = tk.Menu(self.root)
                self.file_menu = tk.Menu(self.menu, tearoff=0)
                self.help_menu = tk.Menu(self.menu, tearoff=0)
                self.cam_frame = tk.Frame(self.root)
                self.controls_frame = tk.Frame(self.root)
                self.info_frame = tk.Frame(self.root)

                self.root.config(menu=self.menu)
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

            # Flags for key presses/releases.
            self.key_q = False
            self.key_w = False
            self.key_e = False
            self.key_r = False
            self.key_a = False
            self.key_s = False
            self.key_d = False
            self.key_f = False

            # Create the layout of the frames.
            self.cam_frame.pack()
            self.controls_frame.pack()
            self.info_frame.pack()

            # Create the layout of the speed scale.
            self.control_speed = tk.Scale(self.controls_frame, from_=1, to=0, resolution=0.1, command=self.callback_scale_speed)
            self.control_speed.set(0.3)
            self.control_speed.grid(row=0, column=0, rowspan=4)

            # Create the layout of the buttons.
            self.control_up = tk.Button(self.controls_frame, text='Up', command=self.callback_button_up)
            self.control_tl = tk.Button(self.controls_frame, text='TL', command=self.callback_button_tl)
            self.control_tr = tk.Button(self.controls_frame, text='TR', command=self.callback_button_tr)
            self.control_left = tk.Button(self.controls_frame, text='Left', command=self.callback_button_left)
            self.control_right = tk.Button(self.controls_frame, text='Right', command=self.callback_button_right)
            self.control_forward = tk.Button(self.controls_frame, text='Forward', command=self.callback_button_forward)
            self.control_backward = tk.Button(self.controls_frame, text='Backward', command=self.callback_button_backward)
            self.control_land = tk.Button(self.controls_frame, text='Land', command=self.callback_button_land)
            self.control_takeoff = tk.Button(self.controls_frame, text='Takeoff', command=self.callback_button_takeoff)
            self.control_down = tk.Button(self.controls_frame, text='Down', command=self.callback_button_down)
            self.control_cam = tk.Button(self.controls_frame, text='Front Camera', command=self.callback_button_cam)

            # Variables for keeping track of sunken buttons.
            self.control_tl_sunk = False
            self.control_tr_sunk = False
            self.control_left_sunk = False
            self.control_right_sunk = False
            self.control_forward_sunk = False
            self.control_backward_sunk = False
            self.control_up_sunk = False
            self.control_down_sunk = False

            self.control_up.grid(row=0, column=2, sticky=tk.S+tk.E+tk.W)
            self.control_tl.grid(row=1, column=1, sticky=tk.S+tk.E+tk.W)
            self.control_forward.grid(row=1, column=2, sticky=tk.S+tk.E+tk.W)
            self.control_tr.grid(row=1, column=3, sticky=tk.S+tk.E+tk.W)
            self.control_left.grid(row=2, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
            self.control_backward.grid(row=2, column=2, sticky=tk.N+tk.S+tk.E+tk.W)
            self.control_right.grid(row=2, column=3, sticky=tk.N+tk.S+tk.E+tk.W)
            self.control_land.grid(row=3, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
            self.control_down.grid(row=3, column=2, sticky=tk.N+tk.S+tk.E+tk.W)
            self.control_takeoff.grid(row=3, column=3, sticky=tk.N+tk.S+tk.E+tk.W)
            self.control_cam.grid(row=4, column=1, columnspan=3, sticky=tk.N+tk.S+tk.E+tk.W)

            # Create the layout of the info labels.
            self.altitude = tk.Label(self.info_frame, text='Altitude:', anchor=tk.W, justify=tk.LEFT, width=90)
            self.position = tk.Label(self.info_frame, text='Position:', anchor=tk.W, justify=tk.LEFT, width=90)
            # self.altitude.pack(fill='x', expand=True)
            # self.position.pack(fill='x', expand=True)

            # # Create the layout of the menu bar.
            self.file_menu.add_command(label='Exit', command=self.root.quit)
            self.help_menu.add_command(label='Help', command=self.callback_help)
            self.help_menu.add_command(label='About', command=self.callback_about)

            self.menu.add_cascade(label='File', menu=self.file_menu)
            self.menu.add_cascade(label='Help', menu=self.help_menu)

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
                    print('Sending command to fly right at speed %0.1f.' % self.fly.drone.speed)
                self.fly.drone.fly_right()
            elif char_pressed == 'a':
                if self.fly.verb >= 1:
                    print('Sending command to fly left at speed %0.1f.' % self.fly.drone.speed)
                self.fly.drone.fly_left()
            elif char_pressed == 's':
                if self.fly.verb >= 1:
                    print('Sending command to fly backward at speed %0.1f.' % self.fly.drone.speed)
                self.fly.drone.fly_backward()
            elif char_pressed == 'w':
                if self.fly.verb >= 1:
                    print('Sending command to fly forward at speed %0.1f.' % self.fly.drone.speed)
                self.fly.drone.fly_forward()
            elif char_pressed == 'q':
                if self.fly.verb >= 1:
                    print('Sending command to turn left at speed %0.1f.' % self.fly.drone.speed)
                self.fly.drone.turn_left()
            elif char_pressed == 'e':
                if self.fly.verb >= 1:
                    print('Sending command to turn right at speed %0.1f.' % self.fly.drone.speed)
                self.fly.drone.turn_right()
            elif char_pressed == 'r':
                if self.fly.verb >= 1:
                    print('Sending command to fly up at speed %0.1f.' % self.fly.drone.speed)
                self.fly.drone.fly_up()
            elif char_pressed == 'f':
                if self.fly.verb >= 1:
                    print('Sending command to fly down at speed %0.1f.' % self.fly.drone.speed)
                self.fly.drone.fly_down()

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

        def key_release(self, event):
            """ Commands the drone to stop when the relevant keys are released.
            """
            char_released = event.keysym
            drone_stop_list = ['d', 'a', 's', 'w', 'q', 'e', 'r', 'f']
            if char_released in drone_stop_list:
                self.fly.drone.stop()

        def callback_help(self):
            filewin = tk.Toplevel(self.root)
            help_text = 'Help'
            label = tk.Label(filewin, text=help_text)
            label.pack()

        def callback_about(self):
            pass

        def callback_scale_speed(self, value):
            self.fly.drone.set_speed(float(value))

        def callback_button_tl(self):
            if self.fly.verb >= 1 and not self.control_tl_sunk:
                print('Sending command to turn left at speed %0.1f.' % self.fly.drone.speed)
            self.fly.drone.turn_left()
            if self.control_tl_sunk:
                self.control_tl.config(relief=tk.RAISED)
                self.fly.drone.stop()
            else:
                self.control_tl.config(relief=tk.SUNKEN)
            self.control_tl_sunk = not self.control_tl_sunk

        def callback_button_tr(self):
            if self.fly.verb >= 1 and not self.control_tr_sunk:
                print('Sending command to turn right at speed %0.1f.' % self.fly.drone.speed)
            self.fly.drone.turn_right()
            if self.control_tr_sunk:
                self.control_tr.config(relief=tk.RAISED)
                self.fly.drone.stop()
            else:
                self.control_tr.config(relief=tk.SUNKEN)
            self.control_tr_sunk = not self.control_tr_sunk

        def callback_button_left(self):
            if self.fly.verb >= 1 and not self.control_left_sunk:
                print('Sending command to fly left at speed %0.1f.' % self.fly.drone.speed)
            self.fly.drone.fly_left()
            if self.control_left_sunk:
                self.control_left.config(relief=tk.RAISED)
                self.fly.drone.fly_left()
            else:
                self.control_left.config(relief=tk.SUNKEN)
            self.control_left_sunk = not self.control_left_sunk

        def callback_button_right(self):
            if self.fly.verb >= 1 and not self.control_right_sunk:
                print('Sending command to fly right at speed %0.1f.' % self.fly.drone.speed)
            self.fly.drone.fly_right()
            if self.control_right_sunk:
                self.control_right.config(relief=tk.RAISED)
                self.fly.drone.stop()
            else:
                self.control_right.config(relief=tk.SUNKEN)
            self.control_right_sunk = not self.control_right_sunk

        def callback_button_forward(self):
            if self.fly.verb >= 1 and not self.control_forward_sunk:
                print('Sending command to fly forward at speed %0.1f.' % self.fly.drone.speed)
            self.fly.drone.fly_forward()
            if self.control_forward_sunk:
                self.control_forward.config(relief=tk.RAISED)
                self.fly.drone.stop()
            else:
                self.control_forward.config(relief=tk.SUNKEN)
            self.control_forward_sunk = not self.control_forward_sunk

        def callback_button_backward(self):
            if self.fly.verb >= 1 and not self.control_backward_sunk:
                print('Sending command to fly backward at speed %0.1f.' % self.fly.drone.speed)
            self.fly.drone.fly_backward()
            if self.control_backward_sunk:
                self.control_backward.config(relief=tk.RAISED)
                self.fly.drone.stop()
            else:
                self.control_backward.config(relief=tk.SUNKEN)
            self.control_backward_sunk = not self.control_backward_sunk

        def callback_button_up(self):
            if self.fly.verb >= 1 and not self.control_up_sunk:
                print('Sending command to fly up at speed %0.1f.' % self.fly.drone.speed)
            self.fly.drone.fly_up()
            if self.control_up_sunk:
                self.control_up.config(relief=tk.RAISED)
                self.fly.drone.stop()
            else:
                self.control_up.config(relief=tk.SUNKEN)
            self.control_up_sunk = not self.control_up_sunk

        def callback_button_down(self):
            if self.fly.verb >= 1 and not self.control_down_sunk:
                print('Sending command to fly down at speed %0.1f.' % self.fly.drone.speed)
            self.fly.drone.fly_down()
            if self.control_down_sunk:
                self.control_down.config(relief=tk.RAISED)
                self.fly.drone.stop()
            else:
                self.control_down.config(relief=tk.SUNKEN)
            self.control_down_sunk = not self.control_down_sunk

        def callback_button_land(self):
            if self.fly.verb >= 1:
                print('Sending command to land.')
            self.fly.drone.land()

        def callback_button_takeoff(self):
            if self.fly.verb >= 1:
                print('Sending command to take off.')
            self.fly.drone.takeoff()

        def callback_button_cam(self):
            if self.fly.verb >= 1:
                print('Sending command to change camera.')
            self.fly.drone.change_camera()

        def update_video(self):
            self.root.after(300, self.update_video)
            frame = self.fly.drone.feat_opt_flow.extract(self.fly.drone.camera.get_frame())
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_frame = Image.fromarray(frame)
            pil_frame = pil_frame.resize((400, 300), Image.ANTIALIAS)
            photo_frame = ImageTk.PhotoImage(pil_frame)
            self.cam_label.config(image=photo_frame)
            self.cam_label.image = photo_frame


class Drone(object):
    """ Encapsulates the drone.
    """
    def __init__(self, controller_url, controller_port, camera_url, camera_port):
        self.controller = Controller(controller_url, controller_port)
        self.camera = Camera(camera_url, camera_port)
        self.speed = 0.3
        self.possible_cameras = ['FRONT_CAMERA', 'BOTTOM_CAMERA']
        self.active_camera = 'FRONT_CAMERA'

        # Create the json template that will be passed to the cmd server.
        self.default_query = {
            'X': 0.0,
            'Y': 0.0,
            'R': 0.0,
            'C': 0,
            'T': False,
            'L': False,
            'S': False
        }

        self.controller.daemon = True
        self.controller.start()

        self.feat_opt_flow = opt_flow.OpticalFlow(self.camera.get_frame())

    def set_speed(self, speed):
        self.speed = speed

    def land(self):
        query = self.default_query.copy()
        query['L'] = True
        query_json = json.dumps(query)
        self.controller.send_query(query_json)

    def takeoff(self):
        query = self.default_query.copy()
        query['T'] = True
        query_json = json.dumps(query)
        self.controller.send_query(query_json)

    def stop(self):
        query = self.default_query.copy()
        query = self.default_query.copy()
        query['S'] = True
        query_json = json.dumps(query)
        self.controller.send_query(query_json)

    def turn_left(self):
        query = self.default_query.copy()
        query['R'] = -self.speed
        query_json = json.dumps(query)
        self.controller.send_query(query_json)

    def turn_right(self):
        query = self.default_query.copy()
        query['R'] = self.speed
        query_json = json.dumps(query)
        self.controller.send_query(query_json)

    def fly_up(self):
        query = self.default_query.copy()
        query['Z'] = self.speed
        query_json = json.dumps(query)
        self.controller.send_query(query_json)

    def fly_down(self):
        query = self.default_query.copy()
        query['Z'] = -self.speed
        query_json = json.dumps(query)
        self.controller.send_query(query_json)

    def fly_forward(self):
        query = self.default_query.copy()
        query['Y'] = self.speed
        query_json = json.dumps(query)
        self.controller.send_query(query_json)

    def fly_backward(self):
        query = self.default_query.copy()
        query['Y'] = -self.speed
        query_json = json.dumps(query)
        self.controller.send_query(query_json)

    def fly_left(self):
        query = self.default_query.copy()
        query['X'] = -self.speed
        query_json = json.dumps(query)
        self.controller.send_query(query_json)

    def fly_right(self):
        query = self.default_query.copy()
        query['X'] = self.speed
        query_json = json.dumps(query)
        self.controller.send_query(query_json)

    def change_camera(self):
        # query = self.fly.default_query.copy()
        # query['C'] = True
        # query_json = json.dumps(query)
        # self.fly.net_thread.send_query(query_json)
        # self.fly.cam = not self.fly.cam
        # if self.fly.cam:
        #     self.control_cam.configure(text='Bottom Camera')
        # else:
        #     self.control_cam.configure(text='Front Camera')
        pass


class Controller(threading.Thread):
    """ Handles sending commands to the drone.
    """
    def __init__(self, controller_url, controller_port):
        threading.Thread.__init__(self)
        self.controller_url = controller_url
        self.controller_port = controller_port

    def run(self):
        # Connect to the node js server.
        try:
            self.cmd_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cmd_soc.connect((self.controller_url, int(self.controller_port)))
        except socket.error as e:
            if e[0] == errno.ECONNREFUSED:
                ConnectionError().print_error()

    def send_query(self, query):
        try:
            self.cmd_soc.send(query)
        except socket.error as e:
            if e[0] == errno.EPIPE:
                ConnectionError().print_error()


class Camera(object):
    """
    """
    def __init__(self, camera_url, camera_port):
        self.camera_url = camera_url
        self.camera_port = camera_port
        self.req = urllib2.Request(self.camera_url + ':' + self.camera_port)
        self.connected = True

    def get_frame(self):
        error_image = cv2.imread('../samples/error_image.jpg')
        frame = error_image
        try:
            if self.connected:
                response = urllib2.urlopen(self.req)
                img_array = np.asarray(bytearray(response.read()), dtype=np.uint8)
                frame = cv2.imdecode(img_array, 1)
        except urllib2.HTTPError:
            if self.connected:
                CameraError().print_error()
                self.connected = False
        except urllib2.URLError:
            if self.connected:
                CameraError().print_error()
                self.connected = False
        finally:
            return frame


def main():
    try:
        DEBUG = 0
        if DEBUG:
            pdb.set_trace()

        # Make the operating system not try and debounce key presses.
        fa = FlyToolArgs()
        fa.parse()
        f = FlyTool(fa.args.gui, fa.args.verb, fa.args.url, fa.args.port, fa.args.stream)
        f.start()
    except KeyboardInterrupt:
        print('\nClosing.')
        sys.exit(1)
    except ArgumentError as e:
        e.print_error()
        sys.exit(1)

if __name__ == '__main__':
    main()
