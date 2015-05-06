#!/usr/bin/env python2.7

""" Implements the DAgger algorithm.
"""

import numpy as np
import sklearn


class DAgger(object):
    """ DAgger algorithm.

        Arguments:
            regressor       The regression algorithm to use. Default uses least
                            squares linear regularized regression
                            (ridge/Tikhonov).
            iterations      The number of iterations of learning.
            beta            The executed policy is an affine combination of the
                            expert's policy and the learned policy.
    """
    def __init__(self, iterations, trajectories, regressor):
        self.regressor = regressor
        self.N = iterations
        self.M = trajectories
        self.D = np.array([])
        self.C = np.array([])

        self.learners = []

        # The level of alpha to use for learning ridge regression. Affects the
        # size of the weights and finds a point on the pareto optimal tradeoff
        # curve.
        self.alpha = 0.5

        self.i = 0  # current iteration
        self.j = 0  # current trajectory

    def aggregate(self):
        """ Aggregate the data.
        """
        data_directory = '../data/'

        # Get the dataset corresponding to the current itteration and
        # trajectory.
        for self.j in range(0, self.M):
            data_filename = data_directory + 'data_%s_%s.data' % (self.i, j)
            cmds_filename = data_directory + 'cmds_%s_%s.cmds' % (self.i, j)

            with open(data_filename, 'r') as f:
                data = f.read()

            with open(cmds_filename, 'r') as f:
                cmds = f.read()

            data = np.loadtxt(data)
            cmds = np.loadtxt(cmds)
            self.D = np.vcat((self.D, data))
            self.C = np.vcat((self.C, cmds))

    def get_current_itteration(self):
        return self.i

    def get_current_trajectory(self):
        return self.j

    def train(self):
        """ Trains the ridge regressor on the aggregate of the data.
        """
        self.i += 1
        learner = sklearn.linear_model.Ridge(alpha=self.alpha)
        learner.fit(self.D, self.C) 
        self.learners.append(learner)

    def test(self, x, itteration):
        """ Try to fit the new state to a left/right control input.
        """ 
        return np.dot(x, self.learners[itteration])


def _test_dagger():
    itterations = 2
    trajectories = 1
    data = np.array([[0, 0], [0, 0], [1, 1]])
    cmds = np.array([0, 0.1, 1])
    d = Dagger(itterations, trajectories, 'tikhonov')
    d.aggregate()

if __name__ == '__main__':
    _test_dagger()
