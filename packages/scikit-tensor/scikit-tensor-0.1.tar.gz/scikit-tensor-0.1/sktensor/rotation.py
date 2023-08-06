import logging
import numpy as np
from numpy import eye, diag, dot
from numpy.linalg import svd

def orthomax(X, tol=1e-7, maxIter=250, gamma=1):
    n,m = X.shape
    Y = np.copy(X)
    T = eye(m)

    if 0 <= gamma <= 1:
        D = 0
        for k in xrange(maxIter):
            Dold = D
            tmp0 = (Y**2).sum(axis=0)
            tmp1 = n*(Y**3)
            U, S, Vt = svd(dot(X.T, tmp1 - dot(gamma*Y, diag(tmp0))))
            T = dot(U, Vt)
            D = S.sum()
            Y = dot(X, T)
            if abs(D - Dold)/D < tol:
                break
    else :

        raise NotImplementedError('Not implemented for gamma not in [0,1]')
    return Y, T

