#!/usr/bin/env python2.7

""" History features.
"""

import numpy as np


class CmdHistory(object):
    """ Command history features.
    """
    def __init__(self, length, period):
        self.history = np.zeros(4, length)
        self.period = period

    def update(self, cmd, form=False):
        """ Updates the history with the specified command.

            Argument form specifies specifies whether the command has been
            transformed into a vector or whether it is the same form as that
            which is sent to the drone.
        """
        if self.history.qsize() == self.length:
            np.roll(self.history, 1, 1)
            np.roll(self.period, 1, 0)
            cmd_vec = cmd if form else np.transpose(np.array([cmd['X'], cmd['Y'], cmd['Z'], cmd['R']]))
            self.history[:, 0] = cmd_vec

    def extract(self, img):
        """ Extracts the command history features.

            To Do: Conduct experimental tests to see what kind of filter to use.
        """
        # Pass the history through a low pass filter.
        fc = 0.1                        # cutoff frequency (fraction of sample rate)
        b = 0.01                        # transition bandwidth
        N = int(np.ceil((4/b)))
        N = N if N % 2 else N + 1       # make sure N is odd
        n = np.arange(N)

        # Compute sinc filter.
        h = np.sinc(2 * fc * (n - (N - 1) / 2.))

        # Compute Blackman window.
        w = 0.42 - 0.5 * np.cos(2 * np.pi * n / (N - 1)) + \
            0.08 * np.cos(4 * np.pi * n / (N - 1))

        # Multiply sinc filter with window.
        h = h * w

        # Normalize to get unity gain.
        h = h/np.sum(h)

        # Convolve the filter with the signal.
        feat = np.convolve(self.cmd_history, h)
        return feat


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
    length = 10
    timestamp = 0.1
    cmd_history = CmdHistory(length, timestamp)

    # Create some test commands.
s = np.convolve(s, h)
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
