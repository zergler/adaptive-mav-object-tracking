#!/usr/bin/env python2.7

""" A tool for extracting features from the drone.
"""

import io
import socket
import struct
import argparse
import sys

from PIL import Image

from optical_flow import OpticalFlow
from laws_mask import LawsMask
from radon_transform import RadonTransform
from struct_tensor_stats import StructTensorStats
from cmd_history import CmdHistory

DEBUG = 0
try:
    import pdb
except ImportError:
    DEBUG = 0


class Error(Exception):
    """ Base exception class.
    """
    pass


class FeatureExtractArgs(object):
    """ Argument parser for feature extraction tool.
    """
    def __init__(self):
        # Basic info.
        self.version = 1.0
        self.name = 'feature_extract'
        self.date = '02/21/15'
        self.author = 'Igor Janjic'
        self.organ = 'Graduate Research at Virginia Tech'
        self.desc = 'A tool for extracting features from monocular images.'
        self.epil = 'Application %s version %s. Created by %s on %s for %s.' % (self.name, self.version, self.author, self.date, self.organ)

        # Arguments help.
        self.help_help = 'Show this help message and exit.'
        self.streams_help = 'Port of the image stream for the front and bottom camera seperated by a comma.'

        # Argparser.
        self.arg_parser = argparse.ArgumentParser(prog=self.name, description=self.desc, epilog=self.epil, add_help=False)
        required_args = self.arg_parser.add_argument_group('Required arguments', '')
        optional_args = self.arg_parser.add_argument_group('Optional arguments', '')

        optional_args.add_argument('-h', '--help', action='help', help=self.help_help)
        required_args.add_argument('-s', '--streams', type=str, dest='streams', required=True, help=self.streams_help, metavar='\b')

    def parse(self):
        self.args = self.arg_parser.parse_args()


class FeatureExtract(object):
    """ Implements feature extraction using a png image stream.
    """
    def __init__(self, front_stream, down_stream):
        self.m_optical_flow = OpticalFlow()
        self.m_laws_mask = LawsMask()
        self.m_radon_transform = RadonTransform()
        self.m_struct_tensor_stats = StructTensorStats()
        self.m_cmd_history = CmdHistory()

        # Connect a client socket to my_server:8000 (change my_server to the
        # hostname of your server)
        front_client_socket = socket.socket()
        front_client_socket.connect(('192.168.1.2', front_stream))

        # Make a file-like object out of the connection
        connection = front_client_socket.makefile('wb')
        try:
            while True:
                # Read the length of the image as a 32-bit unsigned int. If the
                # length is zero, quit the loop
                image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
                if not image_len:
                    break
                # Construct a stream to hold the image data and read the image
                # data from the connection
                image_stream = io.BytesIO()
                image_stream.write(connection.read(image_len))
                # Rewind the stream, open it as an image with PIL and do some
                # processing on it
                image_stream.seek(0)
                image = Image.open(image_stream)
                print('Image is %dx%d' % image.size)
                image.verify()
                print('Image is verified')
        finally:
            connection.close()
            front_client_socket.close()

    def extract(self):
        pass


def main():
    if DEBUG:
        pdb.set_trace()
    args = FeatureExtractArgs()
    args.parse()
    args = args.args

    # Make sure the arguments are valid.
    try:
        streams = args.streams.split(',')
        front_stream = int(streams[0])
        down_stream  = int(streams[1])
    except ValueError:
        print('error: bad stream')
        sys.exit(1)
    try:
        pdb.set_trace()
        fe = FeatureExtract(front_stream, down_stream)
        fe.extract()
    except Error as e:
        print(e.msg)
        sys.exit(1)
    except KeyboardInterrupt:
        print('\nClosing.')


if __name__ == '__main__':
    main()
