import numpy as np
np.seterr(all='raise')

from .. import PeriodicKernel
from .util import opt, rand_params, seed, allclose
from .test_kernels import check_params, check_jacobian, check_hessian
from .test_kernels import check_dK_dtheta, check_d2K_dtheta2

seed()

EPS = opt['eps']
N_BIG = opt['n_big_test_iters']
N_SMALL = opt['n_small_test_iters']
DTHETA = opt['dtheta']


def make_random_kernel():
    h, w, p = rand_params('h', 'w', 'p')
    kernel = PeriodicKernel(h, w, p)
    return kernel

######################################################################


def test_kernel_params():
    seed()
    for i in xrange(N_BIG):
        params = rand_params('h', 'w', 'p')
        yield check_params, PeriodicKernel, params


def test_K():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    dx = x[:, None] - x[None, :]

    def check_K(kernel):
        K = kernel(x, x)
        h, w, p = kernel.params
        pdx = (h ** 2) * np.exp(-2. * (np.sin(dx / (2. * p)) ** 2) / (w ** 2))
        assert allclose(pdx, K)

    for i in xrange(N_BIG):
        kernel = make_random_kernel()
        yield check_K, kernel


def test_sym_K():
    x = np.linspace(-2, 2, 3)
    dx = x[:, None] - x[None, :]

    def check_sym_K(params):
        kernel = PeriodicKernel(*params)
        K = kernel(x, x)
        sym_K = kernel.sym_K
        Ks = np.empty_like(K)
        for i in xrange(x.size):
            for j in xrange(x.size):
                Ks[i, j] = sym_K.evalf(subs={
                    'd': dx[i, j],
                    'h': params[0],
                    'w': params[1],
                    'p': params[2]
                })

        assert allclose(Ks, K)

    yield (check_sym_K, (1, 1, 1))
    yield (check_sym_K, (1, 2, 2))
    yield (check_sym_K, (2, 1, 0.5))
    yield (check_sym_K, (0.5, 0.5, 1))


def test_jacobian():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_jacobian, kernel, x)


def test_hessian():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_hessian, kernel, x)


def test_dK_dh():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_dK_dtheta, kernel, x, 'h', 0)


def test_dK_dw():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_dK_dtheta, kernel, x, 'w', 1)


def test_dK_dp():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_dK_dtheta, kernel, x, 'p', 2)


def test_d2K_dhdh():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_d2K_dtheta2, kernel, x, 'h', 'h', 0)


def test_d2K_dhdw():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_d2K_dtheta2, kernel, x, 'h', 'w', 1)


def test_d2K_dhdp():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_d2K_dtheta2, kernel, x, 'h', 'p', 2)


def test_d2K_dwdh():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_d2K_dtheta2, kernel, x, 'w', 'h', 0)


def test_d2K_dwdw():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_d2K_dtheta2, kernel, x, 'w', 'w', 1)


def test_d2K_dwdp():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_d2K_dtheta2, kernel, x, 'w', 'p', 2)


def test_d2K_dpdh():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_d2K_dtheta2, kernel, x, 'p', 'h', 0)


def test_d2K_dpdw():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_d2K_dtheta2, kernel, x, 'p', 'w', 1)


def test_d2K_dpdp():
    seed()
    x = np.linspace(-2*np.pi, 2*np.pi, 16)
    for i in xrange(N_SMALL):
        kernel = make_random_kernel()
        yield (check_d2K_dtheta2, kernel, x, 'p', 'p', 2)
