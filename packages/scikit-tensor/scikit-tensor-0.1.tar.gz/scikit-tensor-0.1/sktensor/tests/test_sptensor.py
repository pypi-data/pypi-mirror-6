import numpy as np
from numpy import ones, zeros, array, setdiff1d, allclose
from numpy.random import randint
from sktensor.dtensor import dtensor
from sktensor.sptensor import sptensor, fromarray
from nose.tools import assert_equal, assert_true, raises
from .fixtures import ttm_fixture, sptensor_rand_fixture

ttm_fixture(__name__)
sptensor_rand_fixture(__name__)


def setup_diagonal():
    """
    Setup data for a 20x20x20 diagonal tensor
    """
    n = 20
    shape = (n, n, n)
    subs = [np.arange(0, shape[i]) for i in range(len(shape))]
    vals = ones(n)
    return tuple(subs), vals, shape


def test_init():
    """
    Creation of new sptensor objects
    """
    T = sptensor(subs, vals, shape)
    assert_equal(len(shape), T.ndim)
    assert_true((array(shape) == T.shape).all())

    T = sptensor(subs, vals)
    tshape = array(subs).max(axis=1) + 1
    assert_equal(len(subs), len(T.shape))
    assert_true((tshape == array(T.shape)).all())


def test_init_diagonal():
    subs, vals, shape = setup_diagonal()
    T = sptensor(subs, vals, shape)
    assert_equal(len(shape), T.ndim)
    assert_true((array(shape) == T.shape).all())

    T = sptensor(subs, vals)
    assert_equal(len(subs), len(T.shape))
    assert_true((shape == array(T.shape)).all())


@raises(ValueError)
def test_non2Dsubs():
    sptensor(randint(0, 10, 18).reshape(3, 3, 2), ones(10))


@raises(ValueError)
def test_nonEqualLength():
    sptensor(subs, ones(len(subs) + 1))


def test_unfold():
    Td = dtensor(zeros(shape, dtype=np.float32))
    Td[subs] = vals

    for i in range(len(shape)):
        rdims = [i]
        cdims = setdiff1d(range(len(shape)), rdims)[::-1]
        Md = Td.unfold(i)

        T = sptensor(subs, vals, shape, accumfun=lambda l: l[-1])

        Ms = T.unfold(rdims, cdims)
        assert_equal(Md.shape, Ms.shape)
        assert_true((allclose(Md, Ms.toarray())))

        Ms = T.unfold(rdims)
        assert_equal(Md.shape, Ms.shape)
        assert_true((allclose(Md, Ms.toarray())))

        Md = Md.T
        Ms = T.unfold(rdims, cdims, transp=True)
        assert_equal(Md.shape, Ms.shape)
        assert_true((allclose(Md, Ms.toarray())))


def test_fold():
    T = sptensor(subs, vals, shape)
    for i in range(len(shape)):
        X = T.unfold([i]).fold()
        assert_equal(shape, tuple(T.shape))
        assert_equal(len(shape), len(T.subs))
        assert_equal(len(subs), len(T.subs))
        assert_equal(X, T)
        for j in range(len(subs)):
            subs[j].sort()
            T.subs[j].sort()
            assert_true((subs[j] == T.subs[j]).all())


def test_ttm():
    S = sptensor(T.nonzero(), T.flatten(), T.shape)
    Y2 = S.ttm(U, 0)
    assert_equal((2, 4, 2), Y2.shape)
    assert_true((Y == Y2).all())


def test_ttv_sparse_result():
    # Test case by Andre Panisson to check return type of sptensor.ttv
    subs = (
        array([0, 1, 0, 5, 7, 8]),
        array([2, 0, 4, 5, 3, 9]),
        array([0, 1, 2, 2, 1, 0])
    )
    vals = array([1, 1, 1, 1, 1, 1])
    S = sptensor(subs, vals, shape=[10, 10, 3])

    sttv = S.ttv((zeros(10), zeros(10)), modes=[0, 1])
    assert_equal(type(sttv), sptensor)
    # sparse tensor should return only nonzero vals
    assert_true((allclose(np.array([]), sttv.vals)))
    assert_true((allclose(np.array([]), sttv.subs)))
    assert_equal(sttv.shape, (3,))


def test_ttv():
    result = array([
        [70, 190],
        [80, 200],
        [90, 210]
    ])

    X = fromarray(T)
    v = array([1, 2, 3, 4])
    Xv = X.ttv(v, 1)

    assert_equal((3, 2), Xv.shape)
    assert_true((Xv == result).all())


def test_sttm_me():
    S = sptensor(T.nonzero(), T.flatten(), T.shape)
    S.ttm_me(U, [1], [0], False)


def test_sp_uttkrp():
    # Test case by Andre Panisson, sparse ttv
    # see issue #3
    S = sptensor(subs, vals, shape)
    U = []
    for shp in shape:
        U.append(np.zeros((shp, 5)))
    SU = S.uttkrp(U, mode=0)
    assert_equal(SU.shape, (25, 5))

def test_getitem():
    subs = (
        array([0, 1, 0, 5, 7, 8]),
        array([2, 0, 4, 5, 3, 9]),
        array([0, 1, 2, 2, 1, 0])
    )
    vals = array([1, 2, 3, 4, 5, 6])
    S = sptensor(subs, vals, shape=[10, 10, 3])
    assert_equal(0, S[1, 1, 1])
    assert_equal(0, S[1, 2, 3])
    for i in range(len(vals)):
        assert_equal(vals[i], S[subs[0][i], subs[1][i], subs[2][i]])

def test_add():
    subs = (
        array([0, 1, 0]),
        array([2, 0, 2]),
        array([0, 1, 2])
    )
    vals = array([1, 2, 3])
    S = sptensor(subs, vals, shape=[3, 3, 3])
    D = np.arange(27).reshape(3, 3, 3)
    T = S - D
    for i in range(3):
        for j in range(3):
            for k in range(3):
                assert_equal(S[i, j, k] - D[i, j, k], T[i, j, k])
