#!/usr/bin/env python

"""Plotting methods.

This module contains various plotting methods.

"""

from __future__ import division

import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate

from wyrm import tentensystem as tts


def plot_scalp(v, channel):
    """Plot the values v for channel ``channel`` on a scalp."""

    channelpos = [tts.channels[c] for c in channel]
    points = [calculate_stereographic_projection(i) for i in channelpos]
    x = [i[0] for i in points]
    y = [i[1] for i in points]
    z = v
    X, Y, Z = interpolate_2d(x, y, z)
    plt.clf()
    vmin, vmax = 0, .5
    plt.contour(X, Y, Z, 20, vmin=vmin, vmax=vmax)
    plt.contourf(X, Y, Z, 20, vmin=vmin, vmax=vmax)
    #plt.clabel(im)
    #plt.colorbar()
    plt.gca().add_artist(plt.Circle((0, 0), radius=1, linewidth=3, fill=False))
    plt.plot(x, y, 'bo')
    for i in zip(channel, zip(x,y)):
        plt.annotate(i[0], i[1])


def plot_channels(dat, chanaxis=-1, otheraxis=-2):
    """Plot all channels for a continuous.

    Parameters
    ----------
    dat : Data

    """
    ax = []
    n_channels = dat.data.shape[chanaxis]
    for i, chan in enumerate(dat.axes[chanaxis]):
        if i == 0:
            a = plt.subplot(10, n_channels / 10 + 1, i + 1)
        else:
            a = plt.subplot(10, n_channels / 10 + 1, i + 1, sharex=ax[0], sharey=ax[0])
        ax.append(a)
        x, y =  dat.axes[otheraxis], dat.data.take([i], chanaxis)
        a.plot(dat.axes[otheraxis], dat.data.take([i], chanaxis).squeeze())
        a.set_title(chan)
        plt.axvline(x=0)
        plt.axhline(y=0)


def plot_spectrum(spectrum, freqs):
    plt.plot(freqs, spectrum, '.')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('[dl]')


def plot_spectrogram(spectrogram, freqs):
    extent = 0, len(spectrogram), freqs[0], freqs[-1]
    plt.imshow(spectrogram.transpose(),
        aspect='auto',
        origin='lower',
        extent=extent,
        interpolation='none')
    plt.colorbar()
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time')


def calculate_stereographic_projection(p):
    """Calculate the stereographic projection.

    Given a unit sphere with radius ``r = 1`` and center at the origin.
    Project the point ``p = (x, y, z)`` from the sphere's South pole (0,
    0, -1) on a plane on the sphere's North pole (0, 0, 1).

    The formula is:

        P' = P * (2r / (r + z))

    Parameters
    ----------
    p : [float, float]
        The point to be projected in cartesian coordinates.

    Returns
    -------
    x, y : float, float
        The projected point on the plane.

    """
    # P' = P * (2r / r + z)
    mu = 1 / (1 + p[2])
    x = p[0] * mu
    y = p[1] * mu
    return x, y


def interpolate_2d(x, y, z):
    """Interpolate missing points on a plane.

    Parameters
    ----------
    x, y, z : equally long lists of floats
        1d arrays defining points like ``p[x, y] = z``

    Returns
    -------
    X, Y, Z : 1d array, 1d array, 2d array
        ``Z`` is a 2d array ``[min(x)..max(x), [min(y)..max(y)]`` with
        the interpolated values as values.

    """
    X = np.linspace(min(x), max(x))
    Y = np.linspace(min(y), max(y))
    X, Y = np.meshgrid(X, Y)
    #f = interpolate.interp2d(x, y, z)
    #Z = f(X[0, :], Y[:, 0])
    f = interpolate.LinearNDInterpolator(zip(x, y), z)
    Z = f(X, Y)
    return X, Y, Z
