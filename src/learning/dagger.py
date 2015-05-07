#!/usr/bin/env python2.7

""" Implements the DAgger algorithm.
"""

import json
import numpy as np
from sklearn.linear_model import Ridge


class DAgger(object):
    """ DAgger algorithm.
    """
    def __init__(self, iteration, learner):
        self.learner = learner
        self.iteration = iteration

        self.learners = []

        # The level of alpha to use for learning ridge regression. Affects the
        # size of the weights and finds a point on the pareto optimal tradeoff
        # curve.
        self.alpha = 0.5

        # Load the previous aggregate.
        self.aggregate_features_filename = './data/aggregate_features.data'
        self.aggregate_cmds_filename = './data/aggregate_cmds.data'

        # Load the current data.
        self.current_directory = './data/%s/' % self.iteration

        # Load the features into numpy.
        try:
            self.features = self.load_features(self.aggregate_features_filename)
        except IOError:
            self.features = ''

        # Load the cmds into numpy.
        try:
            self.cmds = self.load_cmds(self.aggregate_cmds_filename)
        except IOError:
            self.cmds = ''

    def aggregate(self):
        """ Aggregate the data.
        """
        # Get the dataset corresponding to the current itteration.
        cur_trajectory = 1
        while True:
            features_filename = self.current_directory + '%s/features.data' % cur_trajectory
            cmds_filename = self.current_directory + '%s/expert_cmds.data' % cur_trajectory
            try:
                cur_features = self.load_features(features_filename)
                cur_cmds = self.load_cmds(cmds_filename)
                self.features += cur_features
                self.cmds += cur_cmds
                cur_trajectory += 1
            except:
                break

        # Write the data to the aggregate file.
        pdb.set_trace()
        with open(self.aggregate_features_filename, 'w') as f:
            f.write(self.features) 
        with open(self.aggregate_cmds_filename, 'w') as f:
            f.write(self.cmds)

    def load_features(self, filename):
        with open(filename, 'r') as f:
            features_str = f.read()
        return features_str

    def parse_features(self, features_str):
        features_np = None
        features_str = features_str.split('\n')
        features_str = [i for i in features_str if i != '']
        for i in range(0, len(features_str)):
            cur_features_str = features_str[i].split(' ')
            cur_features_np = np.loadtxt(cur_features_str)
            features_np = np.vstack((features_np, cur_features_np)) if features_np is not None else cur_features_np
        return features_np

    def load_cmds(self, filename):
        # Only uses X for now.
        with open(filename, 'r') as f:
            cmds_str = f.read()
        return cmds_str

    def parse_cmds(self, cmds_str):
        cmds_json = cmds_str.split('\n')
        cmds_json = [i for i in cmds_json if i != '']
        cmds = []
        for i in range(0, len(cmds_json)):
            cmd_json = cmds_json[i]
            cmd = json.loads(cmd_json)
            cmds.append(cmd['X'])
        cmds = np.array([cmds])
        cmds = cmds.transpose()
        return cmds

    def get_current_itteration(self):
        return self.i

    def get_current_trajectory(self):
        return self.j

    def train(self):
        """ Trains the ridge regressor on the aggregate of the data.
        """
        # Load the aggregate data.
        aggregate_features_str = self.load_features(self.aggregate_features_filename)
        aggregate_cmds_str = self.load_cmds(self.aggregate_cmds_filename)
        aggregate_features = self.parse_features(aggregate_features_str)
        aggregate_cmds = self.parse_cmds(aggregate_cmds_str)

        learner = Ridge(alpha=self.alpha)
        learner.fit(aggregate_features, aggregate_cmds)
        self.learners.append(learner)

    def test(self, x, itteration):
        """ Try to fit the new state to a left/right control input.
        """ 
        x_value = self.learners[i].predict(x)


def _test_dagger():
    pdb.set_trace()
    iteration = 1
    d = DAgger(iteration, 'tikhonov')
    d.train()

if __name__ == '__main__':
    import pdb
    _test_dagger()
