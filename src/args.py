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
        desc = 'A tool that allows the user to fly the Parrot AR Drone 2.0 '\
               'easily using the keyboard or a gamepad remote USB controller '\
               'connected to the computer. The tool is used to train a '\
               'learning algorithm by dataset aggregation (DAgger).'
        epil = 'Application %s version %s. Created by %s on %s for %s.' % (name, version, author, date, organ)

        # Arguments help.
        train_help = "Training mode trains the drone with a specific learning "\
                     "algorithm for the given iteration and trajectory. "
        test_help = "Testing mode tests the drone on a specific trajectory "\
                    "and given learning algorithm trained on the given "\
                    "iteration."
        exec_help = 'Execution mode executes a given policy and collects data.'
        ann_help = "Annotate mode allows the user to specify the "\
                   "expert's policy at each iteration and trajectory of "\
                   "learning."
        address_help = 'The addresses of the controller server and receiver '\
                       'server with the form ip:port. The port can range '\
                       'between 9000 and 9500.'
        learning_help = "The type of learning algorithm to use. Use 'tkhonov' "\
                        "for Tikhonov regression or 'ordinary_least_squares' "\
                        "for ordinary least squares linear regression."
        iterations_help = 'The total number of iterations to include in '\
                          'learning.'
        iteration_help = 'The current iteration of learning.'
        trajectory_help = 'The current trajectory that will be learned.'

        help_help = 'Show this help message and exit.'
        gui_help = "Use this flag if you want to use the GUI to view the "\
                   "drone's camera. Default is to not launch the GUI."
        verbosity_help = 'Increase the output verbosity.'

        # Argparser.
        self.arg_parser = argparse.ArgumentParser(prog=name, description=desc, epilog=epil, add_help=False)
        optional_args = self.arg_parser.add_argument_group('Optional arguments', '')
        optional_args.add_argument('-h', '--help', action='help', help=help_help)
        optional_args.add_argument('-g', '--gui', action='store_true', default=False, help=gui_help)
        optional_args.add_argument('-v', '--verbosity', action='count', default=0, help=verbosity_help)


        # Subparser.
        sub_title = 'Subcommands'
        sub_desc = "Valid subcommands are either 'train', 'test', 'exec' or 'annotate'."
        subparsers = self.arg_parser.add_subparsers(title=sub_title,
                                                    description=sub_desc,
                                                    dest='command', help='')

        train_parser = subparsers.add_parser('train', help=train_help, add_help=False)
        train_opt_args = train_parser.add_argument_group('Optional arguments', '')
        train_opt_args.add_argument('-h', '--help', action='help', help=help_help)
        
        train_pos_args = train_parser.add_argument_group('Training arguments', '')
        train_pos_args.add_argument('iterations', type=int, help=iterations_help)
        train_pos_args.add_argument('learning', type=str, help=learning_help)

        test_parser = subparsers.add_parser('test', help=test_help, add_help=False)
        test_opt_args = test_parser.add_argument_group('Optional arguments', '')
        test_opt_args.add_argument('-h', '--help', action='help', help=help_help)

        test_pos_args = test_parser.add_argument_group('Testing arguments', '')
        test_pos_args.add_argument('address', type=str, nargs=2, help=address_help)
        test_pos_args.add_argument('learning', type=str, help=learning_help)
        test_pos_args.add_argument('iteration', type=int, help=iteration_help)
        test_pos_args.add_argument('trajectory', type=int, help=trajectory_help)

        exec_parser = subparsers.add_parser('exec', help=train_help, add_help=False)
        exec_opt_args = exec_parser.add_argument_group('Optional arguments', '')
        exec_opt_args.add_argument('-h', '--help', action='help', help=help_help)

        exec_pos_args = exec_parser.add_argument_group('Training arguments', '')
        exec_pos_args.add_argument('address', type=str, nargs=2, help=address_help)
        exec_pos_args.add_argument('learning', type=str, help=learning_help)
        exec_pos_args.add_argument('iteration', type=int, help=iteration_help)
        exec_pos_args.add_argument('trajectory', type=int, help=trajectory_help)

        ann_parser = subparsers.add_parser('annotate', help=ann_help, add_help=False)
        ann_opt_args = ann_parser.add_argument_group('Optional arguments', '')
        ann_opt_args.add_argument('-h', '--help', action='help', help=help_help)

        ann_pos_args = ann_parser.add_argument_group('Annotation arguments', '')
        ann_pos_args.add_argument('iteration', type=int, help=iteration_help)
        ann_pos_args.add_argument('trajectory', type=int, help=trajectory_help)

        
    def parse(self):
        self.args = self.arg_parser.parse_args()

        # Parse the address
        if self.args.command == 'train':
            self._parse_learning()
        elif self.args.command == 'test' or self.args.command == 'exec':
            self._parse_address(0)
            self._parse_address(1)
            self._parse_learning()
            self._parse_iteration()
            self._parse_trajectory()
        elif self.args.command == 'annotate':
            self._parse_iteration()
            self._parse_trajectory()

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

    def _parse_iteration(self):
        iteration = self.args.iteration
        if iteration <= 0:
            raise debug.Error('args', 'iteration %s is not a positive integer' % iteration)

    def _parse_trajectory(self):
        trajectory = self.args.trajectory
        if trajectory <= 0:
            raise debug.Error('args', 'trajectory %s is not a positive integer' % trajectory)


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
