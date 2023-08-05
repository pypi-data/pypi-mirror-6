from __future__ import division

import unittest

import numpy as np
from scipy.fftpack import rfft, rfftfreq
from scipy.signal import butter

from wyrm.types import Data
from wyrm.processing import lfilter
from wyrm.processing import swapaxes


class TestLFilter(unittest.TestCase):

    def setUp(self):
        # create some data
        fs = 100
        dt = 5
        self.freqs = [2, 7, 15]
        amps = [30, 10, 2]
        t = np.linspace(0, dt, fs*dt)
        data = np.sum([a * np.sin(2*np.pi*t*f) for a, f in zip(amps, self.freqs)], axis=0)
        data = data[:, np.newaxis]
        data = np.concatenate([data, data], axis=1)
        channel = np.array(['ch1', 'ch2'])
        self.dat = Data(data, [t, channel], ['time', 'channel'], ['s', '#'])
        self.dat.fs = fs

    def test_bandpass(self):
        """Band pass filtering."""
        # bandpass around the middle frequency
        fn = self.dat.fs / 2
        b, a = butter(4, [6 / fn, 8 / fn], btype='band')
        ans = lfilter(self.dat, b, a)
        # the amplitudes
        fourier = np.abs(rfft(ans.data, axis=0) * 2 / self.dat.data.shape[0])
        ffreqs = rfftfreq(ans.data.shape[0], 1/ans.fs)
        # check if the outer freqs are damped close to zero
        # freqs...
        for i in self.freqs[0], self.freqs[-1]:
            # buckets for freqs
            for j in fourier[ffreqs == i]:
                # channels
                for k in j:
                    self.assertAlmostEqual(k, 0., delta=.1)

    def test_lfilter_copy(self):
        """lfilter must not modify argument."""
        cpy = self.dat.copy()
        fn = self.dat.fs / 2
        b, a = butter(4, [6 / fn, 8 / fn], btype='band')
        lfilter(self.dat, b, a)
        self.assertEqual(cpy, self.dat)

    def test_lfilter_swapaxes(self):
        """lfilter must work with nonstandard timeaxis."""
        fn = self.dat.fs / 2
        b, a = butter(4, [6 / fn, 8 / fn], btype='band')
        dat = lfilter(swapaxes(self.dat, 0, 1), b, a, timeaxis=1)
        dat = swapaxes(dat, 0, 1)
        dat2 = lfilter(self.dat, b, a)
        self.assertEqual(dat, dat2)


if __name__ == '__main__':
    unittest.main()
