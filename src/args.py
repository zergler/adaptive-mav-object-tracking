#!/usr/bin/python2

""" Argument parser for the flying tool.
"""

import argparse
import debug
import socket


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
        desc = 'A tool that allows the user to fly the Parrot AR Drone 2.0 easily using the keyboard or a gamepad remote USB controller connected to the computer. The tool is used to train a learning algorithm by dataset aggregation (DAgger).'
        epil = 'Application %s version %s. Created by %s on %s for %s.' % (name, version, author, date, organ)

        # Arguments help.
        address_help = 'The addresses of the controller server and receiver server with the form ip:port. The port can range between 9000 and 9500.'
        learning_help = "The type of learning algorithm to use. Use 'tkhonov' for Tikhonov regression or 'ordinary_least_squares' for ordinary least squares linear regression."
        iterations_help = 'The number of iterations of learning to do.'
        trajectories_help = 'The number of trajectories to include per iteration of learning.'
        frame_rate_help = 'The number of times per second to query the camera for images. Default and minimum is 1 frame/s.'
        remote_rate_help = 'The number of times per second to query the remote for commands. Default and minimum is 10 query/s.'
        nav_rate_help = 'The number of times per second to query the receiver for navigation data. Default and minimum is 1 query/s.'

        help_help = 'Show this help message and exit.'
        gui_help = "Use this flag if you want to use the GUI to view the drone's camera. Default is to not launch the GUI."
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

        optional_args.add_argument('-f', '--frame-rate', default=1, type=int, help=frame_rate_help)
        optional_args.add_argument('-r', '--remote-rate', default=10, type=int, help=remote_rate_help)
        optional_args.add_argument('-n', '--nav-rate', default=1, type=int, help=nav_rate_help)

    def parse(self):
        self.args = self.arg_parser.parse_args()

        # Parse the address
        self._parse_address(0)
        self._parse_address(1)

        # Parse the learning argument.
        self._parse_learning()

        # Parse the iterations argument.
        self._parse_iterations()

        # Parse the trajectories argument.
        self._parse_trajectories()

        # Parse rate arguments.
        self._parse_rate(0)
        self._parse_rate(1)
        self._parse_rate(2)

    def _parse_address(self, i):
        assert i == 0 or i == 1
        if i == 0:
            server = 'command'
        elif i == 1:
            server = 'receiver'

        # Try to split the command server address string into ip and port.
        address = self.args.address[i].split(':')
        if len(address) != 2:
            raise debug.Error('args', 'the address of the %s server does not have a valid port' % server)
        else:
            # Make sure the ip is valid (this will throw an error if it's not).
            if address[0] == 'localhost':
                address[0] = '127.0.0.1'
            try:
                socket.inet_aton(address[0])
            except socket.error:
                raise debug.Error('args', 'the address of the %s server does not have a valid ip' % server)
            # Make sure the port is valid.
            try:
                port = int(address[1])
                if port not in range(9000, 9501):
                    raise debug.Error('args', 'the address of the %s server has a port %s not in the valid range 9000 to 9500' % (server, port))
            except ValueError:
                raise debug.Error('args', 'the address of the %s server does not have a valid port' % server)

    def _parse_learning(self):
        learning = self.args.learning
        if learning != 'tikhonov' and learning != 'ordinary_least_squares':
            raise debug.Error('args', "%s is not 'tikhonov' or 'ordinary_least_squares" % learning)

    def _parse_iterations(self):
        iterations = self.args.iterations
        if iterations <= 0:
            raise debug.Error('args', 'iteration %s is not a positive integer' % iterations)

    def _parse_trajectories(self):
        trajectories = self.args.trajectories
        if trajectories <= 0:
            raise debug.Error('args', 'trajectory %s is not a positive integer' % trajectories)

    def _parse_rate(self, i):
        assert i in range(0, 3)
        if i == 0:
            rate_type = 'frame'
            rate = self.args.frame_rate
        elif i == 1:
            rate_type = 'remote'
            rate = self.args.remote_rate
        else:
            rate_type = 'navigation'
            rate = self.args.nav_rate

        if rate <= 0:
            raise debug.Error('args', '%s rate %s is not a positive integer' % (rate_type, rate))


def _test_fly_args():
    pdb.set_trace()
    fa = FlyArgs()
    try:
        fa.parse()
    except debug.Error as e:
        e.print_error()
    else:
        print('Passed arguments work.')

if __name__ == '__main__':
    import pdb
    _test_fly_args()
