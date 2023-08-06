#! /usr/bin/env python

from __future__ import division

from timeside.core import *
from timeside.decoder import *
from timeside.analyzer import *
from timeside.encoder import *
from timeside.component import *

from unit_timeside import *
from tools import tmp_file_sink
import os.path


class TestTranscodingStreaming(unittest.TestCase):
    "Test transcoding and streaming"

    def setUp(self):
        self.source = os.path.join(os.path.dirname(__file__),
                                   "samples/sweep.wav")
        self.test_duration = True
        self.test_channels = True
        self.filesize_delta = None

    def testMp3(self):
        "Test conversion to mp3"
        self.encoder_function = Mp3Encoder
        self.filesize_delta = 156

    def testOgg(self):
        "Test conversion to ogg"
        self.encoder_function = VorbisEncoder

    def testWebM(self):
        "Test conversion to webm"
        self.encoder_function = WebMEncoder
        self.test_duration = False  # webmmux encoder with streamable=true
                                    # does not return a valid duration

    def tearDown(self):
        decoder = FileDecoder(self.source)

        file_extension = '.' + self.encoder_function.file_extension()

        self.target_filesink = tmp_file_sink(prefix=self.__class__.__name__,
                                             suffix=file_extension)

        self.target_appsink = tmp_file_sink(prefix=self.__class__.__name__,
                                            suffix=file_extension)

        encoder = self.encoder_function(self.target_filesink, streaming=True)
        pipe = (decoder | encoder)

        with open(self.target_appsink, 'w') as f:
            for chunk in pipe.stream():
                f.write(chunk)

        decoder_encoded = FileDecoder(self.target_filesink)

        pipe2 = ProcessPipe(decoder_encoded)
        pipe2.run()

        import os
        filesink_size = os.path.getsize(self.target_filesink)
        appsink_size = os.path.getsize(self.target_appsink)

        os.unlink(self.target_filesink)
        os.unlink(self.target_appsink)
        #print decoder.channels(), decoder.samplerate(), written_frames
        #print media_channels

        if self.test_channels:
            self.assertEqual(decoder.channels(), decoder_encoded.channels())
        else:
            self.assertEqual(2, decoder_encoded.channels())  # voaacenc bug ?

        self.assertEqual(decoder.samplerate(),
                         decoder_encoded.samplerate())

        if self.test_duration:
            self.assertAlmostEqual(decoder.input_duration,
                                   decoder_encoded.input_duration,
                                   delta=0.2)
        self.assertAlmostEqual(filesink_size, appsink_size,
                               delta=self.filesize_delta)

if __name__ == '__main__':
    unittest.main(testRunner=TestRunner())
