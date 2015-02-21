#!/usr/bin/env python2.7

""" A tool for extracting features from the drone.
"""

import argparse
import sys

from img_feed import ImgFeed
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
        self.stream_help = 'Name of the image stream.'

        # Argparser.
        self.arg_parser = argparse.ArgumentParser(prog=self.name, description=self.desc, epilog=self.epil, add_help=False)
        required_args = self.arg_parser.add_argument_group('Required arguments', '')
        optional_args = self.arg_parser.add_argument_group('Optional arguments', '')

        optional_args.add_argument('-h', '--help', action='help', help=self.help_help)
        required_args.add_argument('-s', '--stream', type=str, dest='stream', required=True, help=self.stream_help, metavar='\b')

    def parse(self):
        self.args = self.arg_parser.parse_args()


class FeatureExtract(object):
    """ Implements feature extraction using a png image stream.
    """
    def __init__(self, feed_name):
        self.m_image_feed = ImgFeed(feed_name)
        self.m_optical_flow = OpticalFlow()
        self.m_laws_mask = LawsMask()
        self.m_radon_transform = RadonTransform()
        self.m_struct_tensor_stats = StructTensorStats()
        self.m_cmd_history = CmdHistory()

    def extract(self):
        pass


def main():
    if DEBUG:
        pdb.set_trace()
    args = FeatureExtractArgs()
    args.parse()
    args = args.args

    try:
        fe = FeatureExtract()
        fe.extract()
    except Error as e:
        print(e.msg)
        sys.exit(1)
    except KeyboardInterrupt:
        print('\nClosing.')


if __name__ == '__main__':
    main()
