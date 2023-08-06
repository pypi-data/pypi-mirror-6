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
import numpy as np
from numpy import zeros, nonzero, dot, ones, eye, diag
from numpy.random import randn, rand
from numpy.linalg import svd
from scipy.linalg import eigh
import time
from .cp import als as cp_als
from .dtensor import dtensor

_log = logging.getLogger('PARAFAC2')

_EPS = np.finfo(np.double).eps
_CP_CONV = 1e-4
_CP_MAXITER = 5
_ITER_SHOW = 100

_DEF_MAXITER = 2500
_DEF_INIT = 'nvecs'
_DEF_CONV = 1e-5

_log_cp = logging.getLogger('CP ALS')
_log_cp.setLevel(logging.WARN)


def parafac2(X, rank, **kwargs):
    # init options
    ainit = kwargs.pop('init', _DEF_INIT)
    maxiter = kwargs.pop('ma_iter', _DEF_MAXITER)
    conv = kwargs.pop('conv', _DEF_CONV)
    if not len(kwargs) == 0:
        raise ValueError('Unknown keywords (%s)' % (kwargs.keys()))

    K, J = len(X), X[0].shape[1]
    F, D, A = __init(X, ainit, J, K, rank)

    fit = oldfit = 0
    exectimes = []
    Y = dtensor(zeros((rank, J, K)))
    for itr in range(maxiter):
        oldfit = fit

        tic = time.clock()
        # compute model
        P = []
        for k in range(K):
            Qk = dot(dot(F, dot(diag(D[k, :]), A.T)), X[k].T)
            P.append(__psqrt(Qk))
            Y[:, :, k] = dot(P[k].T, X[k])

        Z, _, _, _ = cp_als(
            Y, rank, conv=_CP_CONV,
            max_iter=_CP_MAXITER, init=[F, A, D]
        )
        F, A, D = Z.U

        # calculate fit
        fit = 0
        for k in range(K):
            M = dot(dot(P[k], F), dot(diag(D[k, :]), A.T))
            fit += ((X[k] - M) ** 2).sum()

        fitchange = abs(oldfit - fit)
        toc = time.clock()
        exectimes.append(toc - tic)
        if itr % _ITER_SHOW == 0:
            _log.debug(
                '[%3d] fit: %.5f | delta: %7.1e | secs: %.5f' % (
                    itr, fit, fitchange, exectimes[-1]
                )
            )
        if itr > 0 and fitchange < conv:
            break
    return P, F, D, A, fit, itr, exectimes


def __psqrt(A, tol=_EPS):
    U, S, Vt = svd(A, full_matrices=0)
    r = len(nonzero(S > tol)[0])
    if r == 0:
        return zeros(A.T.shape)
    else:
        return dot(U[:, :r], Vt[:r, :]).T


def __init(X, init, J, K, rank):
    if init == 'nvecs':
        XtX = dot(X[0].T, X[0])
        for k in range(1, K):
            XtX += dot(X[k].T, X[k])
        evals, A = eigh(XtX, eigvals=(J - rank, J - 1))
        D = ones((K, rank)) + randn(K, rank) / 10
        F = eye(rank)
    elif init == 'random':
        A = rand(J, rank)
        D = rand(K, rank)
        F = eye(rank)
    return F, D, A
