import numba
import numpy as np
import pandas as pd

# Numba can be a pain to install. If you do not have numba, the functions 
# will be left in their original, uncompiled form. 
try:
    from numba import jit
except ImportError:
    def jit(arg):
        def _f(f):
            return f 
        return _f

@jit('i8(f8[:],f8,f8)')
def _identify_initial_trend(X, up_thresh, down_thresh):
    x_0 = X[0]
    
    for t in range(1, len(X)):
        if X[t] / x_0 - 1 > up_thresh:
            return -1
        if X[t] / x_0 - 1 < down_thresh:
            return 1
        
    return 0

@jit('f8[:](f8[:],f8,f8)')
def zigzag(X, up_thresh, down_thresh):
    """
    Filters prices to find the peaks and valleys of a sequence assuming that
    a movement is only a movement if it exceeds it's respective threshold.

    returns: 
       an array with 0 indicating no pivot and -1,1 indicating valley and peak 
       respectively

    note:
       The last pivot may not be a real pivot. The last element is always added
       because it is easy to forget about that value in time series data
       and it can skew your results. The first element is also guarenteed to be
       marked as a pivot, for similar easons. They may be discarded in some
       cases.
    """
    pivots = np.zeros_like(X)
    
    initial_trend = _identify_initial_trend(X, up_thresh, down_thresh)
    trend = initial_trend
    last_pivot_t = 0
    last_pivot_x = X[0]
    
    for t in range(1, len(X)):
        x = X[t]
        r = x / last_pivot_x - 1.

        if trend == -1:
            if r > up_thresh:
                pivots[last_pivot_t] = trend
                trend = 1
                last_pivot_x = x
                last_pivot_t = t
            elif x < last_pivot_x:
                last_pivot_x = x
                last_pivot_t = t
        else:
            if r < down_thresh:
                pivots[last_pivot_t] = trend
                trend = -1
                last_pivot_x = x
                last_pivot_t = t
            elif x > last_pivot_x:
                last_pivot_x = x
                last_pivot_t = t
    
    # _identify_initial_trend determined which would come first a up_thresh or 
    # down_thresh movement. The central algorithm automatically takes care
    # of attributing the correct peak or valley; however, the question of 
    # remains: what do you do if the first peak or valley does not occur
    # at t=0. I've chosen to ascribe the opposite type (in the sense of p/v)
    # to the first pivot in this case. This seems like the strategy least likely
    # to introduce error. If need be, you discard the t[0] if this is a bad 
    # bias.
    if pivots[0] == 0:
        pivots[0] = -initial_trend
    
    # The last entry in the sequence is marked as a pivot. This is to avoid 
    # introducing errors where a huge uptrend or downtrend occured but it is
    # invisible because it never terminated.
    pivots[len(X)-1] = trend

    # If there was not a single valid segment, return the entire segment as 
    # the peak and valley.
    if np.sum(pivots != 0) < 2:
        if X[0] > X[1]:
            pivots[0] = 1
            pivots[len(X)-1] = -1
        else:
            pivots[0] = -1
            pivots[len(X)-1] = 1
            
    return pivots

def partition_on_pivots(X, pivots):
    """
    Given a sequence of data, X, and the output of zigzag, pivots, split the 
    data into segments of [last_pivot, next_pivot). 

    This function is useful for statistically interrogating pivots to 
    identify any statistically identifiable differences (other than the mean,
    of course.)
    """
    is_break = pivots != 0
    splits = np.arange(len(is_break))[is_break]
    if(len(splits) < 2): 
        return [X]
    return np.split(X, splits[:-1])[1:]

def compute_segment_returns(X, pivots):
    """
    Computes the pivot-to-pivot returns for each segment. 
    """
    pivot_points = X[pivots != 0]
    return pivot_points[1:] / pivot_points[:-1] - 1.0

@numba.jit('f8(f8[:])')
def max_drawdown(X):
    """
    Returns the maximum drawdown of sequence X. The value returned is the 
    absolute value. If the sequence is increasing, the maximum drawdown is 0.
    """
    mdd = 0
    peak = X[0]
    for x in X:
        if x > peak: 
            peak = x
        dd = (peak - x) / peak
        if dd > mdd:
            mdd = dd
    return mdd

@numba.jit('f8[:](f8[:])')
def pivots_to_modes(pivots):
    """
    Given an array of pivots (computed by zigzag), return the interpolated 
    modes of -1 or 1 for downtrend and uptrend respectively between each
    pivot.
    """
    modes = np.zeros_like(pivots)
    last_pivot = pivots[0]
    modes[0] = -last_pivot
    for i in range(1, len(pivots)):
        x = pivots[i]
        if x != 0:
            last_pivot = -x
        modes[i] = last_pivot
    return modes
