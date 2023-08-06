# Copyright (C) 2013 Maximilian Nickel <mnick@mit.edu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import time
import numpy as np
from numpy import array, dot, zeros, eye
from numpy.random import rand
from numpy.linalg import solve
from sktensor.core import nvecs, norm

_log = logging.getLogger('RESCAL3')
__DEF_MAXITER = 500
__DEF_INIT = 'nvecs'
__DEF_CONV = 1e-5
#__DEF_TTM = ttm

# machine epsilon
eps = np.finfo(np.float).eps


def rescal3_als(X, rankA, rankR, **kwargs):
    # init options
    ainit = kwargs.pop('init', __DEF_INIT)
    maxIter = kwargs.pop('maxIter', __DEF_MAXITER)
    conv = kwargs.pop('conv', __DEF_CONV)
    dtype = kwargs.pop('dtype', X.dtype)
    num_A_updates = kwargs.pop('num_A_updates', 1)
    normalize = kwargs.pop('normalize', False)
    if not len(kwargs) == 0:
        raise ValueError('Unknown keywords (%s)' % (kwargs.keys()))

    normX = norm(X)

    A, R, G = __init(ainit, X, rankA, rankR, dtype)
    AtA = dot(A.T, A)
    RtR = dot(R.T, R)
    fit = 0
    exectimes = []
    for itr in range(maxIter):
        tic = time.clock()
        fitold = fit

        # compute A
        for _ in range(num_A_updates):
            A = updateA(X, A, R, G, AtA, RtR)
            AtA = dot(A.T, A)

        # compute R
        R = updateR(X, A, R, G, AtA)
        RtR = dot(R.T, R)

        # compute G
        G = updateG(X, A, R, AtA, RtR)

        # compute fit
        normresidual = norm(X - G.ttm([A, A, R]))
        fit = 1 - (normresidual / normX)
        fitchange = abs(fitold - fit)
        exectimes.append(time.clock() - tic)

        _log.debug(
            '[%3d] fit: %.5f | delta: %7.1e | secs: %.5f' %
            (itr, fit, fitchange, exectimes[-1])
        )
        if itr > 0 and fitchange < conv:
            break

        if itr > 1 and normalize:
            G = G / norm(G)
            #A = A / sqrt(sum(A ** 2, axis=0))
            #R = R / sqrt(sum(R ** 2, axis=0))
    return G, A, R


def updateA(X, A, R, G, AtA, RtR):
    N, rank = A.shape
    B = zeros((N, rank))
    C = zeros((rank, rank))
    Git = zeros((rank, rank * R.shape[1])).T
    U = [A, A, R]
    V = [AtA, AtA, RtR]
    for i in [0, 1]:
        Git = G.unfold(i).T
        B += dot(X.ttm(U, i, transp=True, without=True).unfold(i), Git)
        C += dot(G.ttm(V, i, without=True).unfold(i), Git)
    I = eye(rank) * eps
    #A = dot(B, inv(C + I))
    A = solve(I + C.T, B.T).T
    return A


def updateR(X, A, R, G, AtA):
    Git = G.unfold(2).T
    B = dot(X.ttm([A, A, R], 2, transp=True, without=True).unfold(2), Git)
    C = dot(G.ttm([AtA, AtA, None], [0, 1]).unfold(2), Git)
    I = eye(R.shape[1]) * eps
    #R = dot(B, inv(C + I))
    R = solve(I + C.T, B.T).T
    return R


def updateG(X, A, R, AtA, RtR):
    B = solve(eye(A.shape[1]) * eps + AtA, A.T)
    C = solve(eye(R.shape[1]) * eps + RtR, R.T)
    #B = dot(inv(AtA + (eye(A.shape[1]) * 1e-9)), A.T)
    #C = dot(inv(RtR + (eye(R.shape[1]) * 1e-9)), R.T)
    G = X.ttm([B, B, C])
    return G


def __init(init, X, rankA, rankR, dtype):
    _log.debug('Initializing A, R')
    if isinstance(init, list):
        A, R = init
    elif init == 'random':
            A = array(rand(X.shape[0], rankA), dtype=dtype)
            R = array(rand(X.shape[2], rankR), dtype=dtype)
            G = array(rand(rankA, rankA, rankR), dtype=dtype)
    elif init == 'nvecs':
            Xt = X.transpose(axes=(1, 0, 2))
            A = array(nvecs(X.concatenate([Xt], axis=2), 0, rankA), dtype=dtype)
            R = array(nvecs(X, 2, rankR), dtype=dtype)
            G = X.ttm([A, A, R], transp=True)
    return A, R, G
