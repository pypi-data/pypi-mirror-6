import logging, time
import numpy as np
from numpy import dot, ones, zeros, diag, kron, outer, array
from numpy.linalg import qr, pinv, norm, solve, inv
from scipy.linalg import eigh
from numpy.random import rand
from scipy.optimize import fmin_l_bfgs_b, fmin_ncg

__DEF_MAXITER = 1000
__DEF_PROJ = True
__DEF_CONV = 1e-5
EPS = 1e-9

_log = logging.getLogger('NN-ASALSAN')
#np.seterr(invalid='raise')


def asalsan(X, rank, **kwargs):
    # init options
    maxIter = kwargs.pop('maxIter', __DEF_MAXITER)
    conv = kwargs.pop('conv', __DEF_CONV)
    if not len(kwargs) == 0:
        raise BaseException( 'Unknown keywords (%s)' % (kwargs.keys()) )

    # init starting points
    D = ones((len(X), rank))
    sz = X[0].shape
    n = sz[0]
    R = rand(rank, rank)
    A = rand(n, rank)

    # perform decomposition
    normX = [norm(M) ** 2 for M in X]
    Xflat = [M.flatten() for M in X]
    M = zeros((n, n))
    normXSum = sum(normX)
    #normX = norm(X)**2
    fit = fitold = f = fitchange = 0
    exectimes = []
    for iters in xrange(maxIter):
        tic = time.clock()
        fitold = fit

        A = __updateA(X, A, D, R)
        R = __updateR(X, A, D, R)
        D, f = __updateD(X, A, D, R)

        # compute fit
        f = 0
        for i in xrange(len(X)):
            M = dot(dot(A, dot(diag(D[i, :]), R)), dot(diag(D[i, :]), A.T))
            f += normX[i] + norm(M)**2 - 2*dot(Xflat[i], M.flatten())
            #f += norm(X[i] - dot(AD, dot(R, AD.T)))**2
        f *= 0.5
        fit = 1 - (f / normXSum)
        fitchange = abs(fitold - fit)

        #A = __normalize(A)
        #R = R / norm(R)
        #D = __normalize(D)

        toc = time.clock()
        exectimes.append(toc - tic)
        _log.debug('[%3d] fit: %.5f | delta: %7.1e | secs: %.5f' % (iters, fit, fitchange, exectimes[-1]))
        if iters > 1 and fitchange < conv:
            break
    return A, R, D, fit, iters, array(exectimes)


def __updateA(X, A, D, R):
    rank = A.shape[1]
    F = zeros((X[0].shape[0], rank))
    E = zeros((rank, rank))

    AtA = dot(A.T, A)
    for i in range(len(X)):
        Dk = diag(D[i, :])
        DRD = dot(Dk, dot(R, Dk))
        DRtD = DRD.T
        F += X[i].dot(dot(A, DRtD)) + X[i].T.dot(dot(A, DRD))
        E += dot(DRD, dot(AtA, DRtD)) + dot(DRtD, dot(AtA, DRD))
    # TODO check if gaussian elimination solution exists
    E = dot(A, E) + EPS
    A = A * (F / E)
    return A


def __updateR(X, A, D, R):
    r = A.shape[1] ** 2
    T = zeros((r, r))
    t = zeros(r)
    for i in range(len(X)):
        AD = dot(A, diag(D[i, :]))
        ADt = AD.T
        tmp = dot(ADt, AD)
        T = T + kron(tmp, tmp)
        tmp = dot(ADt, X[i].dot(AD))
        t = t + tmp.flatten()
    r = A.shape[1]
    # TODO check if this is correct
    #R = solve(T, t).reshape(r,r)
    Rflat = R.flatten()
    T = dot(T, Rflat) + EPS
    R = (Rflat * t / T).reshape(r, r)
    return R


def __updateD(X, A, D, R):
    f = 0
    for i in range(len(X)):
        d = D[i, :]
        u = Updater(X[i], A, R)
        bounds = len(d) * [(0, None)]
        res = fmin_l_bfgs_b(u.updateD_F, d, u.updateD_G, bounds=bounds)
        #res = fmin_ncg(u.updateD_F, d, u.updateD_G, fhess=u.updateD_H, full_output=True, disp=False)
        D[i, :] = res[0]
        f += res[1]
    return D, f


class Updater:
    def __init__(self, Z, A, R):
        self.Z = Z
        self.A = A
        self.R = R
        self.x = None

    def precompute(self, x):
        if self.x is None or (x != self.x).any():
            self.AD = dot(self.A, diag(x))
            self.ADt = self.AD.T
            self.E = self.Z - dot(self.AD, dot(self.R, self.ADt))

    def updateD_F(self, x):
        self.precompute(x)
        return norm(self.E, 'fro') ** 2

    def updateD_G(self, x):
        self.precompute(x)
        g = zeros(len(x))
        Ai = zeros(self.A.shape[0])
        for i in range(len(g)):
            Ai = self.A[:, i]
            g[i] = (self.E * (dot(self.AD, outer(self.R[:, i], Ai)) +
                    dot(outer(Ai, self.R[i, :]), self.ADt))).sum()
        return -2 * g

    def updateD_H(self, x):
        self.precompute(x)
        H = zeros((len(x), len(x)))
        Ai = zeros(self.A.shape[0])
        Aj = zeros(Ai.shape)
        for i in range(len(x)):
            Ai = self.A[:, i]
            ti = dot(self.AD, outer(self.R[:, i], Ai)) + dot(outer(Ai, self.R[i,:]), self.ADt)

            for j in range(i,len(x)):
                Aj = self.A[:,j]
                tj = outer(Ai, Aj)
                H[i, j] = (self.E * (self.R[i,j]*tj + self.R[j,i]*tj.T) - \
                    ti * (dot(self.AD, outer(self.R[:,j], Aj)) + dot(outer(Aj, self.R[j,:]), self.ADt))).sum()
                H[j, i] = H[i, j]
        H *= -2
        return H


def __projectSlices(X, Q):
    X2 = []
    for i in range(len(X)):
        X2.append(Q.T.dot(X[i].dot(Q)))
    return X2


def __normalize(M):
    m = np.sqrt((M ** 2).sum(axis=0))
    m[m == 0] = 1
    return M / m
