#!/usr/bin/env python2.7

""" A tool that allows the user to fly the drone easily from a gui application.
"""

import argparse
import socket
import sys
import threading
import Tkinter as tk
from PIL import ImageTk, Image

DEBUG = 0
try:
    import pdb
except ImportError:
    DEBUG = 0


class Error(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg):
        self.msg = 'error: %s' % msg

    def print_error(self, msg):
        print(self.msg)


class ArgumentError(Error):
    def __init__(self, arg):
        self.msg = "error: argument '%s' is invalid" % arg


class FlyArgs(object):
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
        gui_help = 'Use this flag if you want to use the gui.'
        record_help = 'Use this argument if you want to record the front and bottom camera streams as mpeg. If so, pass the name of the files the streams will be saved in.'
        verb_help = 'Increase the output verbosity.'
        streams_help = 'Port of the image stream for the front and bottom camera seperated by a comma.'

        # Argparser.
        self.arg_parser = argparse.ArgumentParser(prog=name, description=desc, epilog=epil, add_help=False)
        required_args = self.arg_parser.add_argument_group('Required arguments', '')
        optional_args = self.arg_parser.add_argument_group('Optional arguments', '')

        optional_args.add_argument('-h', '--help', action='help', help=help_help)
        optional_args.add_argument('-g', '--gui', dest='gui', action='store_true', default=False, help=gui_help)
        optional_args.add_argument('-v', '--verbosity', dest='verb', action='count', default=0, help=verb_help)
        optional_args.add_argument('-r', '--record', type=str, dest='record', help=record_help, metavar='\b')
        required_args.add_argument('-s', '--streams', type=str, dest='streams', required=True, help=streams_help, metavar='\b')

    def parse(self):
        self.args = self.arg_parser.parse_args()

        # Parse the streams argument.
        self.streams = None
        if self.args.streams is not None:
            try:
                self.streams = self.args.streams.split(',')
                # Make sure the ports are real.
            except ValueError:
                raise ArgumentError(self.args.streams)

        # Parse the record argument.
        self.record = None
        if self.args.record is not None:
            try:
                self.record = self.args.record.split(',')
                # Make sure that the file can be accessed with correct permissions.
            except ValueError:
                raise ArgumentError(self.args.record)


class Fly(object):
    """ Flying tool.
    """
    def __init__(self, gui, verb, record, streams):
        self.verb = verb
        self.fc_port = streams[0] if streams else None
        self.bc_port = streams[1] if streams else None
        self.fc_filename = record[0] if record else None
        self.bc_filename = record[1] if record else None
        self.gui = self.create_gui() if gui else None

    def create_gui(self):
        """ Factory method that builds the GUI and passes the fly object to it.
        """
        return Fly.FlyGUI(self)

    def start(self):
        """ Starts the flying tool.
        """
        if self.verb >= 0:
            print('Parrot AR 2 Flying Tool')
        if self.verb >= 1:
            if self.gui:
                print(':: GUI flag set.')
            print(':: Verbosity set to %d.' % self.verb)
            if self.fc_port and self.bc_port:
                print(':: Accessing front camera stream at port: %s.' % self.fc_port)
                print(':: Accessing bottom camera stream at port: %s.' % self.bc_port)
            if self.fc_filename and self.br_filename:
                print(':: Saving front camera stream to file: %s.' % self.fc_filename)
                print(':: Saving bottom camera stream to file: %s.' % self.br_filename)
        if self.gui:
            self.gui.run()

    class FlyGUI(threading.Thread):
        """ GUI for flying tool.
        """
        def __init__(self, fly):
            threading.Thread.__init__(self)
            self.fly = fly
            self.root = tk.Tk()
            if self.root:
                self.root.resizable(0, 0)  # change this later
                self.root.wm_title("Parrot AR 2 Flying Tool")
                self.menu = tk.Menu(self.root)
                self.file_menu = tk.Menu(self.menu, tearoff=0)
                self.help_menu = tk.Menu(self.menu, tearoff=0)
                self.fc_frame = tk.Frame(self.root)
                self.bc_frame = tk.Frame(self.root)
                self.controls_frame = tk.Frame(self.root)
                self.info_frame = tk.Frame(self.root)

                self.root.config(menu=self.menu)
                self.create_gui()

        def run(self):
            self.root.mainloop()
            sys.exit(0)

        def create_gui(self):
            """ Creates the gui.
            """
            # Create the layout of the frames.
            self.fc_frame.grid(row=0, column=0)
            self.bc_frame.grid(row=0, column=1)
            self.controls_frame.grid(row=1, column=0, columnspan=2)
            self.info_frame.grid(row=2, column=0, columnspan=2)

            # Create the layout of the info labels.
            self.altitude = tk.Label(self.info_frame, text='Altitude:')
            self.position = tk.Label(self.info_frame, text='Position:')
            self.altitude.pack(fill='x')
            self.position.pack(fill='x')

            # # Create the layout of the menu bar.
            self.file_menu.add_command(label='Exit', command=self.root.quit)
            self.help_menu.add_command(label='Help', command=self.help_callback)
            self.help_menu.add_command(label='About', command=self.about_callback)

            self.menu.add_cascade(label='File', menu=self.file_menu)
            self.menu.add_cascade(label='Help', menu=self.help_menu)

            # Test images for frames.
            test_image = Image.open('../samples/test_cameras.jpg')
            test_photo = ImageTk.PhotoImage(test_image)
            fc_test_label = tk.Label(self.fc_frame, image=test_photo)
            fc_test_label.image = test_photo
            bc_test_label = tk.Label(self.bc_frame, image=test_photo)
            bc_test_label.image = test_photo

            # self.world_label.bind('<Configure>', self.resize)
            fc_test_label.pack()
            bc_test_label.pack()

        def help_callback(self):
            filewin = tk.Toplevel(self.root)
            help_text = 'Help'
            label = tk.Label(filewin, text='')
            label.pack()
            pass

        def about_callback(self):
            pass


def main():
    try:
        DEBUG = 0
        if DEBUG:
            pdb.set_trace()
        fa = FlyArgs()
        fa.parse()
        f = Fly(fa.args.gui, fa.args.verb, fa.record, fa.streams)
        f.start()
    except KeyboardInterrupt:
        # Close gui thread!
        print('\nClosing.')
        sys.exit(1)
    except ArgumentError as e:
        e.print_error()
        sys.exit(1)


if __name__ == '__main__':
    main()
