#!/usr/bin/env python2.7

""" History features module.
"""

import numpy as np


def get_spacing(max_length, num_feats, func='linear'):
    """ Creates an array containing indices for spacing a time period.
    """
    if func == 'linear':
        spacing = np.floor(np.linspace(0, np.log10(max_length), num_feats))
    elif func == 'log':
        spacing = np.floor(np.logspace(0, np.log10(max_length), num_feats))
    spacing = [int(i) for i in spacing]
    spacing = np.array(list(set(spacing)))
    return spacing


def low_pass_average(array, spacing):
    """ Passes an array through an averaging low pass filter.
    """
    result = []
    length = spacing.shape
    length = length[0]
    for i in range(0, length):
        time_slice = array[:, 0:spacing[i]]
        if time_slice.shape[1] == 1:
            result = np.vstack((result, time_slice)) if len(result) else time_slice
        else:
            mean = np.mean(time_slice, 1)
            mean.shape = (mean.shape[0], 1)
            result = np.vstack((result, mean))
    return result


def low_pass_sinc_window(array, spacing):
    """ Passes an array through a sinc-window low pass filter.
    """
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

    result = []
    length = spacing.shape
    length = length[0]
    for i in range(0, length):
        time_slice = array[:, 0:spacing[i]]
        if time_slice.shape[1] == 1:
            result = np.vstack((result, time_slice)) if len(result) else time_slice
        else:
            # Convolve the filter with the signal.
            conv = np.convolve(array, h)

            conv.shape = (conv.shape[0], 1)
            result = np.vstack((result, conv))
    return result


class CmdHistory(object):
    """ Command history features.
    """
    def __init__(self, num_feats, max_length):
        self.num_feats = num_feats
        self.max_length = max_length
        self.history = np.zeros((4, max_length))

        # Create the spacing for the exponentially decreasing time periods.
        self.spacing = get_spacing(self.max_length, self.num_feats, func='log')

    def update(self, cmd, form=False):
        """ Updates the history with the specified command.

            Argument form specifies specifies whether the command has been
            transformed into a col vector or whether it is the same form as that
            which is sent to the drone.
        """
        self.history = np.roll(self.history, 1)
        cmd_vec = cmd if form else np.transpose(np.array([cmd['X'], cmd['Y'], cmd['Z'], cmd['R']]))
        self.history[:, 0] = cmd_vec

    def extract(self, low_pass_filter='average'):
        """ Extracts the command history features.

            Filter can be 'average' or 'sinc'.
        """
        if low_pass_filter == 'average':
            func = low_pass_average
        elif low_pass_filter == 'sinc':
            func = low_pass_sinc_window
        feats = func(self.history, self.spacing)
        return feats


class NavHistory(object):
    """ Navigation history features.
    """
    def __init__(self, num_feats, max_length):
        self.num_feats = num_feats
        self.max_length = max_length
        self.history = np.zeros((4, max_length))

        # Create the spacing for the exponentially decreasing time periods.
        self.spacing = get_spacing(self.max_length, self.num_feats, func='log')

    def update(self, navdata, form=False):
        """ Updates the navigation data history with the current navigation
            data.
        """
        # Parse the navigation data getting only the useful info and form it
        # into an array.
        useful_nav_data = []
        if not form:
            useful_nav_data.append(navdata['demo']['altitude'])
            useful_nav_data.append(navdata['demo']['rotation']['pitch'])
            useful_nav_data.append(navdata['demo']['rotation']['roll'])
            useful_nav_data.append(navdata['demo']['rotation']['yaw'])
        
        useful_nav_data = np.array(useful_nav_data)
        self.history = np.roll(self.history, 1)
        self.history[:, 0] = useful_nav_data

    def extract(self, low_pass_filter='average'):
        """ Extracts the navigation history features.

            Filter can be 'average' or 'sinc'.
        """
        if low_pass_filter == 'average':
            func = low_pass_average
        elif low_pass_filter == 'sinc':
            func = low_pass_sinc_window
        feats = func(self.history, self.spacing)
        return feats


def _test_command_history():
    pdb.set_trace()
    num_feats = 7
    max_length = 35
    try:
        cmd_history = CmdHistory(num_feats, max_length)

        # Create some test commands.
        cmds = []
        cmds.append(np.array([-0.5, 0, 0, 0]))
        cmds.append(np.array([-0.4, 0, 0, 0]))
        for cmd in cmds:
            cmd_history.update(cmd, form=True)

        cmd_history_feats = cmd_history.extract()
        print(cmd_history_feats)
    except Exception:
        print(sys.exc_info())


if __name__ == '__main__':
    import pdb
    import sys
    #_test_command_history()
    _test_navigation_history()
