#!/usr/bin/env python2.7

""" Encapsulates an image feed.
"""


class ImgFeed(object):
    """ Encapsulates an image feed.
    """
    def __init__(self, feed_name):
        self.feed_name == feed_name
        self.curFrame = 0

    def get_cur_frame(self):
        pass

    def get_frame(self, frame_num):
        pass
