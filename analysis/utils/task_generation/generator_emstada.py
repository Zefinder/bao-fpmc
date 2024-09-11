#!/usr/bin/python

"""A taskset generator for experiments with real-time task sets

Copyright 2010 Paul Emberson, Roger Stafford, Robert Davis.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY EXPRESS
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are
those of the authors and should not be interpreted as representing official
policies, either expressed or implied, of Paul Emberson, Roger Stafford or
Robert Davis.

Includes Python implementation of Roger Stafford's randfixedsum implementation
http://www.mathworks.com/matlabcentral/fileexchange/9700
Adapted specifically for the purpose of taskset generation with fixed
total utilisation value

Please contact paule@rapitasystems.com or robdavis@cs.york.ac.uk if you have
any questions regarding this software.
"""

import numpy

from utils.task_generation.tasks import *
from math import ceil, floor

import random

NAMED_PERIODS = {
                    'uni-short'     : (3, 33),
                    'uni-moderate'  : (10, 100),
                    'uni-long'      : (50, 250),
                    'uni-broad'     : (1, 1000),
                }

NAMED_PERIOD_DISTRIBUTIONS = [
                                "logunif",
                                "unif",
                             ]


def quantize_params(taskset):
    """After applying overheads, use this function to make
        task parameters integral again."""

    for t in taskset:
        t.cost     = int(ceil(t.cost))
        t.period   = int(floor(t.period))
        t.deadline = int(floor(t.deadline))
        if not min(t.period, t.deadline) or t.density() > 1:
            return False

    return taskset



def ms2us(ms):
    return ms * 1000


def StaffordRandFixedSum(n, u, nsets):

    #deal with n=1 case
    if n == 1:
        return numpy.tile(numpy.array([u]),[nsets,1])

    k = numpy.floor(u)
    s = u
    step = 1 if k < (k-n+1) else -1
    s1 = s - numpy.arange( k, (k-n+1)+step, step )
    step = 1 if (k+n) < (k-n+1) else -1
    s2 = numpy.arange( (k+n), (k+1)+step, step ) - s

    tiny = numpy.finfo(float).tiny
    huge = numpy.finfo(float).max

    w = numpy.zeros((n, n+1))
    w[0,1] = huge
    t = numpy.zeros((n-1,n))

    for i in numpy.arange(2, (n+1)):
        tmp1 = w[i-2, numpy.arange(1,(i+1))] * s1[numpy.arange(0,i)]/float(i)
        tmp2 = w[i-2, numpy.arange(0,i)] * s2[numpy.arange((n-i),n)]/float(i)
        w[i-1, numpy.arange(1,(i+1))] = tmp1 + tmp2;
        tmp3 = w[i-1, numpy.arange(1,(i+1))] + tiny;
        tmp4 = numpy.array( (s2[numpy.arange((n-i),n)] > s1[numpy.arange(0,i)]) )
        t[i-2, numpy.arange(0,i)] = (tmp2 / tmp3) * tmp4 + (1 - tmp1/tmp3) * (numpy.logical_not(tmp4))

    m = nsets
    x = numpy.zeros((n,m))
    rt = numpy.random.uniform(size=(n-1,m)) #rand simplex type
    rs = numpy.random.uniform(size=(n-1,m)) #rand position in simplex
    s = numpy.repeat(s, m)
    j = numpy.repeat(int(k+1), m)
    sm = numpy.repeat(0, m)
    pr = numpy.repeat(1, m)

    for i in numpy.arange(n-1,0,-1): #iterate through dimensions
        e = ( rt[(n-i)-1,...] <= t[i-1,j-1] ) #decide which direction to move in this dimension (1 or 0)
        sx = rs[(n-i)-1,...] ** (1/float(i)) #next simplex coord
        sm = sm + (1-sx) * pr * s/float(i+1)
        pr = sx * pr
        x[(n-i)-1,...] = sm + pr * e
        s = s - e
        j = j - e #change transition table column if required

    x[n-1,...] = sm + pr * s

    #iterated in fixed dimension order but needs to be randomised
    #permute x row order within each column
    for i in range(0,m):
        x[...,i] = x[numpy.random.permutation(n),i]

    return numpy.transpose(x)

def gen_periods(n, nsets, min, max, gran, dist):

    if dist == "logunif":
        periods = numpy.exp(numpy.random.uniform(low=numpy.log(min), high=numpy.log(max+gran), size=(nsets,n)))
    elif dist == "unif":
        periods = numpy.random.uniform(low=min, high=(max+gran), size=(nsets,n))
    elif type(dist) == list:
        # Interpret as set of pre-defined periods to choose from.
        assert nsets == 1
        # avoid numpy.random.choice() because we need to be compatible with 1.6.X
        periods = [random.choice(dist) for _ in range(n)]
        # wrap in numpy types
        periods = numpy.array(periods)
        periods.shape = (1, n)
    else:
        return None

    periods = numpy.floor(periods / gran) * gran

    return periods

# wrapper for generating task sets for use within the schedcat library
# parameters:
#   periods:                one from NAMED_PERIODS (period definitions similar to those used in tasksets.py
#   period_distribution:    'unif' or 'logunif' for uniform or log-based distribution
#   tasks_n:                number of tasks to be generated
#   utilization:            target utilization of the task set to be generated
def gen_taskset(periods, period_distribution, tasks_n, utilization,
                period_granularity=None, scale=ms2us, want_integral=True):
    if periods in NAMED_PERIODS:
        # Look up by name.
        (period_min, period_max) = NAMED_PERIODS[periods]
    else:
        # If unknown, then assume caller specified range manually.
        (period_min, period_max) = periods
    x = StaffordRandFixedSum(tasks_n, utilization, 1)
    if period_granularity is None:
        period_granularity = period_min
        
    periods = gen_periods(tasks_n, 1, period_min, period_max, period_granularity, period_distribution)
    if periods is None:
        raise Exception("Periods could not be generated!")
    
    ts = TaskSystem()

    periods = numpy.maximum(periods[0], max(period_min, period_granularity))

    C = scale(x[0] * periods)

    taskset = numpy.c_[x[0], C / periods, periods, C]
    for t in range(numpy.size(taskset,0)):
        ts.append(SporadicTask(taskset[t][3], scale(taskset[t][2])))

    if want_integral:
        quantize_params(ts)
    return ts
