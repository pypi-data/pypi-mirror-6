#!/usr/bin/python
# -*- coding: utf-8 -*-
from .__init__ import noise_exponential, noise_cross_exponential

def test():
    import numpy as np
    import os
    import sys
    from matplotlib import pylab as plt
    sys.path.append(os.path.realpath(os.path.dirname(__file__)+"/../"))
    from multipletau import autocorrelate, correlate, correlate_numpy
    ## Starting parameters
    N = np.int(np.pi*1e3)
    countrate = 250. * 1e-3 # in Hz
    taudiff = 55. # in us
    deltat = 2e-6 # time discretization [s]
    normalize = True

    # time factor
    taudiff *= deltat

    ##
    ## Autocorrelation
    ##
    print("Creating noise for autocorrelation")
    data = noise_exponential(N, taudiff, deltat=deltat)
    data += - np.average(data)
    if normalize:
        data += countrate
    # multipletau
    print("Performing autocorrelation (multipletau).")
    G = autocorrelate(data, deltat=deltat, normalize=normalize)
    # numpy.correlate for comparison
    if len(data) < 1e5:
        print("Performing autocorrelation (numpy).")
        Gd = correlate_numpy(data, data, deltat=deltat,
                             normalize=normalize)
    # Calculate the expected curve
    x = G[:,0]
    amp = np.correlate(data-np.average(data), data-np.average(data),
                       mode="valid")
    if normalize:
        amp /= len(data) * countrate**2
    y = amp*np.exp(-x/taudiff)

    ##
    ## Cross-correlation
    ##
    print("Creating noise for cross-correlation")
    a, v = noise_cross_exponential(N, taudiff, deltat=deltat)
    a += - np.average(a)
    v += - np.average(v)
    if normalize:
        a += countrate
        v += countrate
    # multipletau
    Gccforw = correlate(a, v, deltat=deltat, normalize=normalize)
    Gccback = correlate(v, a, deltat=deltat, normalize=normalize)
    if len(a) < 1e5:
        print("Performing autocorrelation (numpy).")
        Gdccforw = correlate_numpy(a, v, deltat=deltat, normalize=normalize)
    # Calculate the expected curve
    xcc = Gccforw[:,0]
    ampcc = np.correlate(a-np.average(a), v-np.average(v), mode="valid")

    if normalize:
        ampcc /= len(a) * countrate**2
    ycc = ampcc*np.exp(-xcc/taudiff)


    ##
    ## Plotting
    ##

    # AC
    fig = plt.figure()
    fig.canvas.set_window_title('testing multipletau')
    ax = fig.add_subplot(2,1,1)
    ax.set_xscale('log')
    plt.plot(x, y, "g-", label="input model")
    plt.plot(G[:,0], G[:,1], "r-", label="autocorrelate")
    if len(data) < 1e5:
        plt.plot(Gd[:,0], Gd[:,1] , "b--", label="correlate (numpy)")
    plt.xlabel("lag channel")
    plt.ylabel("autocorrelation")
    plt.legend(loc=0, fontsize='small')
    plt.ylim( -amp*.2, amp*1.2)


    ## CC
    ax = fig.add_subplot(2,1,2)
    ax.set_xscale('log')
    plt.plot(xcc, ycc, "g-", label="input model")
    plt.plot(Gccforw[:,0], Gccforw[:,1], "r-", label="forward")
    if len(data) < 1e5:
        plt.plot(Gdccforw[:,0], Gdccforw[:,1] , "b--", label="forward (numpy)")
    plt.plot(Gccback[:,0], Gccback[:,1], "r--", label="backward")
    plt.xlabel("lag channel")
    plt.ylabel("cross-correlation")
    plt.legend(loc=0, fontsize='small')

    plt.ylim( -ampcc*.2, ampcc*1.2)

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    test()
