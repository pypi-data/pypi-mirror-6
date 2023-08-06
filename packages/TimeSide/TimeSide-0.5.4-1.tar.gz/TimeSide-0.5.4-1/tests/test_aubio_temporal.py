#! /usr/bin/env python

from unit_timeside import *
from timeside.decoder import *
from timeside.analyzer.aubio_temporal import AubioTemporal

class TestAubioTemporal(unittest.TestCase):

    def setUp(self):
        self.analyzer = AubioTemporal()

    def testOnSweep(self):
        "runs on sweep"
        self.source = os.path.join (os.path.dirname(__file__),  "samples", "sweep.wav")

    def testOnGuitar(self):
        "runs on guitar"
        self.source = os.path.join (os.path.dirname(__file__),  "samples", "guitar.wav")

    def tearDown(self):
        decoder = FileDecoder(self.source)
        (decoder | self.analyzer).run()
        results = self.analyzer.results
        #print results
        results.to_yaml()
        results.to_json()
        results.to_xml()

if __name__ == '__main__':
    unittest.main(testRunner=TestRunner())
