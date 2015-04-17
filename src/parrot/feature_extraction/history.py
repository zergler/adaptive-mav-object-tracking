#!/usr/bin/env python2.7

""" History features.
"""

import numpy as np


class CmdHistory(object):
    """ Command history features.
    """
    def __init__(self, num_feats, max_length, period):
        self.num_feats = 7  # does not guarantee there will be 7
        self.max_length = max_length
        self.history = np.zeros((4, max_length))
        self.period = period

        # Create the spacing for the exponentially decreasing time periods.
        spacing = np.floor(np.logspace(0, np.log10(self.max_length), num_feats))
        spacing = [int(i) for i in spacing]
        self.spacing = np.array(list(set(spacing)))

    def update(self, cmd, form=False):
        """ Updates the history with the specified command.

            Argument form specifies specifies whether the command has been
            transformed into a col vector or whether it is the same form as that
            which is sent to the drone.
        """
        self.history = np.roll(self.history, 1)
        cmd_vec = cmd if form else np.transpose(np.array([cmd['X'], cmd['Y'], cmd['Z'], cmd['R']]))
        self.history[:, 0] = cmd_vec

    def extract(self):
        """ Extracts the command history features.

            To Do: Conduct experimental tests to see what kind of filter to use.
        """
        # # Pass the history through a low pass filter.
        # fc = 0.1                        # cutoff frequency (fraction of sample rate)
        # b = 0.01                        # transition bandwidth
        # N = int(np.ceil((4/b)))
        # N = N if N % 2 else N + 1       # make sure N is odd
        # n = np.arange(N)

        # # Compute sinc filter.
        # h = np.sinc(2 * fc * (n - (N - 1) / 2.))

        # # Compute Blackman window.
        # w = 0.42 - 0.5 * np.cos(2 * np.pi * n / (N - 1)) + \
        #     0.08 * np.cos(4 * np.pi * n / (N - 1))

        # # Multiply sinc filter with window.
        # h = h * w

        # # Normalize to get unity gain.
        # h = h/np.sum(h)

        # # Convolve the filter with the signal.
        # feat = np.convolve(self.cmd_history, h)

        # Just compute the average for each of the exponentially decreasing time
        # periods.
        feats = []
        length = self.spacing.shape
        length = length[0]
        for i in range(0, length):
            time_slice = self.history[:, 0:self.spacing[i]]
            if time_slice.shape[1] == 1:
                feats = np.vstack((feats, time_slice)) if len(feats) else time_slice
            else:
                mean = np.mean(time_slice, 1)
                mean.shape = (mean.shape[0], 1)
                feats = np.vstack((feats, mean))
        return feats


class NavHistory(object):
    """ Navigation history features.
    """
    def __init__(self):
        pass

    def update(self, navdata):
        pass

    def extract(self):
        feat = None
        return feat


def _test_command_history():
    pdb.set_trace()
    num_feats = 7
    max_length = 35
    period = 0.1
    cmd_history = CmdHistory(num_feats, max_length, period)

    # Create some test commands.
    cmds = []
    cmds.append(np.array([-0.5, 0, 0, 0]))
    cmds.append(np.array([-0.4, 0, 0, 0]))
    for cmd in cmds:
        cmd_history.update(cmd, form=True)

    cmd_history_feats = cmd_history.extract()
    print(cmd_history_feats)

if __name__ == '__main__':
    import pdb
    _test_command_history()
