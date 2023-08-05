"""
Test for jacobian/hessian functions in Theano
"""
import unittest
from theano.tests  import unittest_tools as utt
from theano import function
import theano
from theano import tensor
import numpy

utt.seed_rng()


def test001_jacobian_vector():
    x = tensor.vector()
    y = x * 2
    rng = numpy.random.RandomState(seed=utt.fetch_seed())

    # test when the jacobian is called with a tensor as wrt
    Jx = tensor.jacobian(y, x)
    f = theano.function([x], Jx)
    vx = rng.uniform(size=(10,)).astype(theano.config.floatX)
    assert numpy.allclose(f(vx), numpy.eye(10) * 2)

    # test when the jacobian is called with a tuple as wrt
    Jx = tensor.jacobian(y, (x,))
    assert isinstance(Jx, tuple)
    f = theano.function([x], Jx[0])
    vx = rng.uniform(size=(10,)).astype(theano.config.floatX)
    assert numpy.allclose(f(vx), numpy.eye(10) * 2)

    # test when the jacobian is called with a list as wrt
    Jx = tensor.jacobian(y, [x])
    assert isinstance(Jx, list)
    f = theano.function([x], Jx[0])
    vx = rng.uniform(size=(10,)).astype(theano.config.floatX)
    assert numpy.allclose(f(vx), numpy.eye(10) * 2)

    # test when the jacobian is called with a list of two elements
    z = tensor.vector()
    y = x * z
    Js = tensor.jacobian(y, [x, z])
    f = theano.function([x, z], Js)
    vx = rng.uniform(size=(10,)).astype(theano.config.floatX)
    vz = rng.uniform(size=(10,)).astype(theano.config.floatX)
    vJs = f(vx, vz)
    evx = numpy.zeros((10, 10))
    evz = numpy.zeros((10, 10))
    numpy.fill_diagonal(evx, vx)
    numpy.fill_diagonal(evz, vz)
    assert numpy.allclose(vJs[0], evz)
    assert numpy.allclose(vJs[1], evx)


def test002_jacobian_matrix():
    x = tensor.matrix()
    y = 2 * x.sum(axis=0)
    rng = numpy.random.RandomState(seed=utt.fetch_seed())
    ev = numpy.zeros((10, 10, 10))
    for dx in xrange(10):
        ev[dx, :, dx] = 2.

    # test when the jacobian is called with a tensor as wrt
    Jx = tensor.jacobian(y, x)
    f = theano.function([x], Jx)
    vx = rng.uniform(size=(10, 10)).astype(theano.config.floatX)
    assert numpy.allclose(f(vx), ev)

    # test when the jacobian is called with a tuple as wrt
    Jx = tensor.jacobian(y, (x,))
    assert isinstance(Jx, tuple)
    f = theano.function([x], Jx[0])
    vx = rng.uniform(size=(10, 10)).astype(theano.config.floatX)
    assert numpy.allclose(f(vx), ev)

    # test when the jacobian is called with a list as wrt
    Jx = tensor.jacobian(y, [x])
    assert isinstance(Jx, list)
    f = theano.function([x], Jx[0])
    vx = rng.uniform(size=(10, 10)).astype(theano.config.floatX)
    assert numpy.allclose(f(vx), ev)

    # test when the jacobian is called with a list of two elements
    z = tensor.matrix()
    y = (x * z).sum(axis=1)
    Js = tensor.jacobian(y, [x, z])
    f = theano.function([x, z], Js)
    vx = rng.uniform(size=(10, 10)).astype(theano.config.floatX)
    vz = rng.uniform(size=(10, 10)).astype(theano.config.floatX)
    vJs = f(vx, vz)
    evx = numpy.zeros((10, 10, 10))
    evz = numpy.zeros((10, 10, 10))
    for dx in xrange(10):
        evx[dx, dx, :] = vx[dx, :]
        evz[dx, dx, :] = vz[dx, :]
    assert numpy.allclose(vJs[0], evz)
    assert numpy.allclose(vJs[1], evx)


def test003_jacobian_scalar():
    x = tensor.scalar()
    y = x * 2
    rng = numpy.random.RandomState(seed=utt.fetch_seed())

    # test when the jacobian is called with a tensor as wrt
    Jx = tensor.jacobian(y, x)
    f = theano.function([x], Jx)
    vx = numpy.cast[theano.config.floatX](rng.uniform())
    assert numpy.allclose(f(vx), 2)

    # test when the jacobian is called with a tuple as wrt
    Jx = tensor.jacobian(y, (x,))
    assert isinstance(Jx, tuple)
    f = theano.function([x], Jx[0])
    vx = numpy.cast[theano.config.floatX](rng.uniform())
    assert numpy.allclose(f(vx), 2)

    # test when the jacobian is called with a list as wrt
    Jx = tensor.jacobian(y, [x])
    assert isinstance(Jx, list)
    f = theano.function([x], Jx[0])
    vx = numpy.cast[theano.config.floatX](rng.uniform())
    assert numpy.allclose(f(vx), 2)

    # test when the jacobian is called with a list of two elements
    z = tensor.scalar()
    y = x * z
    Jx = tensor.jacobian(y, [x, z])
    f = theano.function([x, z], Jx)
    vx = numpy.cast[theano.config.floatX](rng.uniform())
    vz = numpy.cast[theano.config.floatX](rng.uniform())
    vJx = f(vx, vz)

    assert numpy.allclose(vJx[0], vz)
    assert numpy.allclose(vJx[1], vx)


def test004_hessian():
    x = tensor.vector()
    y = tensor.sum(x ** 2)
    Hx = tensor.hessian(y, x)
    f = theano.function([x], Hx)
    vx = numpy.arange(10).astype(theano.config.floatX)
    assert numpy.allclose(f(vx), numpy.eye(10) * 2)
