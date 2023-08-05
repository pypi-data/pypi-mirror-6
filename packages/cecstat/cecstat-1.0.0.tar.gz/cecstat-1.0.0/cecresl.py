#from scipy import stats
import numpy as np


def desSta(the_list):
    mean = np.mean(the_list)
    median = np.median(the_list)

    range = np.ptp(the_list)
    variance = np.var(the_list)
    #ddof-Means Delta Degrees of Freedom
    #http://docs.scipy.org/doc/numpy/reference/generated/numpy.std.html#numpy.std
    #stdDeviation = np.std(the_list, ddof=1)
    #rjust and rjust is used to alignment
    printLeftRightAdj('mean', mean)
    printLeftRightAdj('median', median)
    printLeftRightAdj('range', range)
    printLeftRightAdj('variance', variance)


def printLeftRightAdj(l, r):
    print l.ljust(10), str(r).rjust(10)


desSta([14, 20, 18, 17, 15])
