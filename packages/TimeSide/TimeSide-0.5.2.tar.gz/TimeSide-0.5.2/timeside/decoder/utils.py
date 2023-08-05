# -*- coding: utf-8 -*-

# Copyright (c) 2007-2013 Parisson
# Copyright (c) 2007-2013 Guillaume Pellerin <pellerin@parisson.com>
# Copyright (c) 2010-2013 Paul Brossier <piem@piem.org>
#
# This file is part of TimeSide.

# TimeSide is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# TimeSide is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with TimeSide.  If not, see <http://www.gnu.org/licenses/>.

# Authors:
# Paul Brossier <piem@piem.org>
# Guillaume Pellerin <yomguy@parisson.com>
# Thomas Fillon <thomas@parisson.com>

from __future__ import division

import numpy

class Noise(object):
    """A class that mimics audiolab.sndfile but generates noise instead of reading
    a wave file. Additionally it can be told to have a "broken" header and thus crashing
    in the middle of the file. Also useful for testing ultra-short files of 20 samples."""

    def __init__(self, num_frames, has_broken_header=False):
        self.seekpoint = 0
        self.num_frames = num_frames
        self.has_broken_header = has_broken_header

    def seek(self, seekpoint):
        self.seekpoint = seekpoint

    def get_nframes(self):
        return self.num_frames

    def get_samplerate(self):
        return 44100

    def get_channels(self):
        return 1

    def read_frames(self, frames_to_read):
        if self.has_broken_header and self.seekpoint + frames_to_read > self.num_frames // 2:
            raise IOError()

        num_frames_left = self.num_frames - self.seekpoint
        if num_frames_left < frames_to_read:
            will_read = num_frames_left
        else:
            will_read = frames_to_read
        self.seekpoint += will_read
        return numpy.random.random(will_read)*2 - 1


def path2uri(path):
    """
    Return a valid uri (file scheme) from absolute path name of a file

    >>> path2uri('/home/john/my_file.wav')
    'file:///home/john/my_file.wav'

    >>> path2uri('C:\Windows\my_file.wav')
    'file:///C%3A%5CWindows%5Cmy_file.wav'
    """
    import urlparse, urllib

    return urlparse.urljoin('file:', urllib.pathname2url(path))


def get_uri(source):
    """
    Check a media source as a valid file or uri and return the proper uri
    """

    import gst
    # Is this an valid URI source
    if gst.uri_is_valid(source):
        uri_protocol = gst.uri_get_protocol(source)
        if gst.uri_protocol_is_supported(gst.URI_SRC, uri_protocol):
            return source
        else:
            raise IOError('Invalid URI source for Gstreamer')

    # is this a file?
    import os.path
    if os.path.exists(source):
        # get the absolute path
        pathname = os.path.abspath(source)
        # and make a uri of it
        uri = path2uri(pathname)

        return get_uri(uri)
    else:
        raise IOError('Failed getting uri for path %s: not such file or directoy' % source)

    return uri

def get_media_uri_info(uri):

    from gst.pbutils import Discoverer
    from gst import SECOND as GST_SECOND
    from glib import GError
    #import gobject
    GST_DISCOVER_TIMEOUT = 5000000000L
    uri_discoverer = Discoverer(GST_DISCOVER_TIMEOUT)
    try:
        uri_info = uri_discoverer.discover_uri(uri)
    except  GError as e:
        raise IOError(e)
    info = dict()

    # Duration in seconds
    info['duration'] = uri_info.get_duration() / GST_SECOND

    audio_streams = uri_info.get_audio_streams()
    info['streams'] = []
    for stream in audio_streams:
        stream_info = {'bitrate': stream.get_bitrate (),
                       'channels': stream.get_channels (),
                       'depth': stream.get_depth (),
                       'max_bitrate': stream.get_max_bitrate(),
                       'samplerate': stream.get_sample_rate()
                       }
        info['streams'].append(stream_info)

    return info



if __name__ == "__main__":
    # Run doctest from __main__ and unittest from tests
    from tests.unit_timeside import run_test_module
    # load corresponding tests
    from tests import test_decoder_utils

    run_test_module(test_decoder_utils)

