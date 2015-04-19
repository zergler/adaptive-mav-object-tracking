#!/usr/bin/env python2.7

""" Implements the DAgger algorithm.
"""

import numpy as np


class CameraError(Exception):
    """ Base exception for the module.
    """
    def __init__(self, msg='', warning=False):
        default_header = 'Error: dagger'
        default_error = '%s: an exception occured.' % default_header
        self.msg = default_error if msg == '' else '%s: %s.' % (default_header, msg)
        self.warning = warning

    def print_error(self):
        print(self.msg)


class DAgger(object):
    """ DAgger algorithm.

        Arguments:
            iterations      The number of iterations of learning.
            beta            The executed policy is an affine combination of the
                            expert's policy and the learned policy.
            regressor       The regression algorithm to use. Default uses least
                            squares linear regularized regression
                            (ridge/Tikhonov).
            data_filename   The name of the files containing the data.
            labels_filename The name of the files containing the expert's label
                            for the data.
    """
    def __init__(self, iterations, trajectories, beta, regressor, data_filenames, labels_filenames):
        self.N = iterations
        self.M = trajectories
        self.B = beta
        self.learn = regressor
        self.D = np.array([])
        self.C = np.array([])

        self.i = 0  # current itteration

    def aggregate(self):
        """ Aggregate the data.
        """
        data_directory = '../data/'

        # Get the dataset corresponding to the current itteration and
        # trajectory.
        for j in range(0, self.M):
            data_filename = data_directory + 'data_%s_%s.txt' % (self.i, j)
            cmds_filename = data_directory + 'cmds_%s_%s.txt' % (self.i, j)

            with open(data_filename, 'r') as f:
                data = f.read()

            with open(cmds_filename, 'r') as f:
                cmds = f.read()

            data   = np.loadtxt(data)
            cmds = np.loadtxt(cmds)
            self.D = np.vcat((self.D, data))
            self.C = np.vcat((self.C, cmds))

    def train(self):
        """ Ridge regression code goes here.
        """
        self.i += 1
        policy = None
        return policy
