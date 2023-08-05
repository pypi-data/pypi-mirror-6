__all__ = ["GP"]

import numpy as np
import copy
import matplotlib.pyplot as plt
import scipy.optimize as optim
import warnings

from .ext import gp_c

DTYPE = np.float64
EPS = np.finfo(DTYPE).eps
MIN = np.log(np.exp2(DTYPE(np.finfo(DTYPE).minexp + 4)))


def memoprop(f):
    """
    Memoized property.

    When the property is accessed for the first time, the return value
    is stored and that value is given on subsequent calls. The memoized
    value can be cleared by calling 'del prop', where prop is the name
    of the property.

    """
    fname = f.__name__

    def fget(self):
        if fname not in self._memoized:
            self._memoized[fname] = f(self)
        return self._memoized[fname]

    def fdel(self):
        del self._memoized[fname]

    prop = property(fget=fget, fdel=fdel, doc=f.__doc__)
    return prop


class GP(object):
    r"""
    Gaussian Process object.

    Parameters
    ----------
    K : :class:`kernels.Kernel`
        Kernel object
    x : numpy.ndarray
        :math:`n` array of input locations
    y : numpy.ndarray
        :math:`n` array of input observations
    s : number (default=0)
        Standard deviation of observation noise

    """

    def __init__(self, K, x, y, s=0):
        r"""
        Initialize the GP.

        """
        self._memoized = {}
        self._x = None
        self._y = None
        self._s = None
        self.n = 0

        #: Kernel for the gaussian process, of type
        #: :class:`kernels.Kernel`
        self.K = K
        self._params = np.empty(K.params.size + 1, dtype=DTYPE)

        self.x = x
        self.y = y
        self.s = s

    @property
    def x(self):
        r"""
        Vector of input locations.

        Returns
        -------
        x : numpy.ndarray
            :math:`n` array, where :math:`n` is the number of
            locations.

        """
        return self._x

    @x.setter
    def x(self, val):
        if np.any(val != self._x):
            self._memoized = {}
            self._x = val.astype(DTYPE)
            self.n, = self.x.shape

    @property
    def y(self):
        r"""
        Vector of input observations.

        Returns
        -------
        y : numpy.ndarray
            :math:`n` array, where :math:`n` is the number of
            observations.

        """
        return self._y

    @y.setter
    def y(self, val):
        if np.any(val != self._y):
            self._memoized = {}
            self._y = val.astype(DTYPE)
            if self.y.shape != (self.n,):
                raise ValueError("invalid shape for y: %s" % str(self.y.shape))

    @property
    def s(self):
        r"""
        Standard deviation of the observation noise for the gaussian
        process.

        Returns
        -------
        s : numpy.float64

        """
        return self._s

    @s.setter
    def s(self, val):
        if val != self._s:
            self._memoized = {}
            self._s = DTYPE(val)

    @property
    def params(self):
        r"""
        Gaussian process parameters.

        Returns
        -------
        params : numpy.ndarray
           Consists of the kernel's parameters, `self.K.params`, and the
           observation noise parameter, :math:`s`, in that order.

        """
        self._params[:-1] = self.K.params
        self._params[-1] = self._s
        return self._params

    @params.setter
    def params(self, val):
        if np.any(self.params != val):
            self._memoized = {}
            self.K.params = val[:-1]
            self.s = val[-1]

    def copy(self):
        """
        Create a copy of the gaussian process object.

        Returns
        -------
        gp : :class:`gp.GP`
            New gaussian process object

        """
        new_gp = GP(self.K.copy(), self.x, self.y, s=self.s)
        new_gp._memoized = copy.deepcopy(self._memoized)
        return new_gp

    @memoprop
    def Kxx(self):
        r"""
        Kernel covariance matrix :math:`\mathbf{K}_{xx}`.

        Returns
        -------
        Kxx : numpy.ndarray
            :math:`n\times n` covariance matrix

        Notes
        -----
        The entry at index :math:`(i, j)` is defined as:

        .. math:: K_{x_ix_j} = K(x_i, x_j) + s^2\delta(x_i-x_j),

        where :math:`K(\cdot{})` is the kernel function, :math:`s` is the
        standard deviation of the observation noise, and :math:`\delta`
        is the Dirac delta function.

        """
        x, s = self._x, self._s
        K = self.K(x, x)
        K += np.eye(x.size, dtype=DTYPE) * (s ** 2)
        return K

    @memoprop
    def Kxx_J(self):
        x = self._x
        return self.K.jacobian(x, x)

    @memoprop
    def Kxx_H(self):
        x = self._x
        return self.K.hessian(x, x)

    @memoprop
    def Lxx(self):
        r"""
        Cholesky decomposition of the kernel covariance matrix.

        Returns
        -------
        Lxx : numpy.ndarray
            :math:`n\times n` lower triangular matrix

        Notes
        -----
        The value is :math:`\mathbf{L}_{xx}`, such that
        :math:`\mathbf{K}_{xx} = \mathbf{L}_{xx}\mathbf{L}_{xx}^\top`.

        """
        return np.linalg.cholesky(self.Kxx)

    @memoprop
    def inv_Lxx(self):
        r"""
        Inverse cholesky decomposition of the kernel covariance matrix.

        Returns
        -------
        inv_Lxx : numpy.ndarray
            :math:`n\times n` matrix

        Notes
        -----
        The value is :math:`\mathbf{L}_{xx}^{-1}`, such that:

        .. math:: \mathbf{K}_{xx} = \mathbf{L}_{xx}\mathbf{L}_{xx}^\top

        """
        return np.linalg.inv(self.Lxx)

    @memoprop
    def inv_Kxx(self):
        r"""
        Inverse kernel covariance matrix, :math:`\mathbf{K}_{xx}^{-1}`.

        Returns
        -------
        inv_Kxx : numpy.ndarray
            :math:`n\times n` matrix

        """
        Li = self.inv_Lxx
        return np.dot(Li.T, Li)

    @memoprop
    def inv_Kxx_y(self):
        r"""
        Dot product of the inverse kernel covariance matrix and of
        observation vector.

        Returns
        -------
        inv_Kxx_y : numpy.ndarray
            :math:`n` array

        Notes
        -----
        This is defined as :math:`\mathbf{K}_{xx}^{-1}\mathbf{y}`.

        """
        return np.dot(self.inv_Kxx, self._y)

    @memoprop
    def log_lh(self):
        r"""
        Marginal log likelihood.

        Returns
        -------
        log_lh : numpy.float64
            Marginal log likelihood

        Notes
        -----
        This is the log likelihood of observations :math:`\mathbf{y}`
        given locations :math:`\mathbf{x}` and kernel parameters
        :math:`\theta`. It is defined by Eq. 5.8 of [RW06]_:

        .. math::

            \log{p(\mathbf{y} | \mathbf{x}, \mathbf{\theta})} = -\frac{1}{2}\mathbf{y}^\top \mathbf{K}_{xx}^{-1}\mathbf{y} - \frac{1}{2}\log{\left|\mathbf{K}_{xx}\right|}-\frac{d}{2}\log{2\pi},

        where :math:`d` is the dimensionality of :math:`\mathbf{x}`.

        """
        y = self._y
        K = self.Kxx
        Kiy = self.inv_Kxx_y
        return DTYPE(gp_c.log_lh(y, K, Kiy))

    @memoprop
    def lh(self):
        r"""
        Marginal likelihood.

        Returns
        -------
        lh : numpy.float64
            Marginal likelihood

        Notes
        -----
        This is the likelihood of observations :math:`\mathbf{y}` given
        locations :math:`\mathbf{x}` and kernel parameters
        :math:`\theta`. It is defined as:

        .. math::

            p(\mathbf{y} | \mathbf{x}, \mathbf{\theta}) = \left(2\pi\right)^{-\frac{d}{2}}\left|\mathbf{K}_{xx}\right|^{-\frac{1}{2}}\exp\left(-\frac{1}{2}\mathbf{y}^\top\mathbf{K}_{xx}^{-1}\mathbf{y}\right)

        where :math:`d` is the dimensionality of :math:`\mathbf{x}`.

        """
        llh = self.log_lh
        if llh < MIN:
            return 0
        else:
            return np.exp(self.log_lh)

    @memoprop
    def dloglh_dtheta(self):
        r"""
        Derivative of the marginal log likelihood.

        Returns
        -------
        dloglh_dtheta : numpy.ndarray
            :math:`n_\theta`-length vector of derivatives, where
            :math:`n_\theta` is the number of parameters (equivalent to
            ``len(self.params)``).

        Notes
        -----
        This is a vector of first partial derivatives of the log
        likelihood with respect to its parameters :math:`\theta`. It is
        defined by Equation 5.9 of [RW06]_:

        .. math::

            \frac{\partial}{\partial\theta_i}\log{p(\mathbf{y}|\mathbf{x},\theta)}=\frac{1}{2}\mathbf{y}^\top\mathbf{K}_{xx}^{-1}\frac{\partial\mathbf{K}_{xx}}{\partial\theta_i}\mathbf{K}_{xx}^{-1}\mathbf{y}-\frac{1}{2}\mathbf{tr}\left(\mathbf{K}_{xx}^{-1}\frac{\partial\mathbf{K}_{xx}}{\partial\theta_i}\right)

        """

        y = self._y
        dloglh = np.empty(len(self.params))
        Ki = self.inv_Kxx
        Kj = self.Kxx_J
        Kiy = self.inv_Kxx_y
        gp_c.dloglh_dtheta(y, Ki, Kj, Kiy, self._s, dloglh)
        return dloglh

    @memoprop
    def dlh_dtheta(self):
        r"""
        Derivative of the marginal likelihood.

        Returns
        -------
        dlh_dtheta : numpy.ndarray
            :math:`n_\theta`-length vector of derivatives, where
            :math:`n_\theta` is the number of parameters (equivalent to
            ``len(self.params)``).

        Notes
        -----
        This is a vector of first partial derivatives of the likelihood
        with respect to its parameters :math:`\theta`.

        """

        y = self._y
        dlh = np.empty(len(self.params))
        Ki = self.inv_Kxx
        Kj = self.Kxx_J
        Kiy = self.inv_Kxx_y
        lh = self.lh
        gp_c.dlh_dtheta(y, Ki, Kj, Kiy, self._s, lh, dlh)
        return dlh

    @memoprop
    def d2lh_dtheta2(self):
        r"""
        Second derivative of the marginal likelihood.

        Returns
        -------
        d2lh_dtheta2 : numpy.ndarray
            :math:`n_\theta`-length vector of derivatives, where
            :math:`n_\theta` is the number of parameters (equivalent to
            ``len(self.params)``).

        Notes
        -----
        This is a matrix of second partial derivatives of the likelihood
        with respect to its parameters :math:`\theta`.

        """

        y = self._y
        Ki = self.inv_Kxx
        Kj = self.Kxx_J
        Kh = self.Kxx_H
        Kiy = self.inv_Kxx_y
        lh = self.lh
        dlh = self.dlh_dtheta
        d2lh = np.empty((len(self.params), len(self.params)))
        gp_c.d2lh_dtheta2(y, Ki, Kj, Kh, Kiy, self._s, lh, dlh, d2lh)
        return d2lh

    def Kxoxo(self, xo):
        r"""
        Kernel covariance matrix of new sample locations.

        Parameters
        ----------
        xo : numpy.ndarray
            :math:`m` array of new sample locations

        Returns
        -------
        Kxoxo : numpy.ndarray
            :math:`m\times m` covariance matrix

        Notes
        -----
        This is defined as :math:`K(\mathbf{x^*}, \mathbf{x^*})`, where
        :math:`\mathbf{x^*}` are the new locations.

        """
        return self.K(xo, xo)

    def Kxxo(self, xo):
        r"""
        Kernel covariance matrix between given locations and new sample
        locations.

        Parameters
        ----------
        xo : numpy.ndarray
            :math:`m` array of new sample locations

        Returns
        -------
        Kxxo : numpy.ndarray
            :math:`n\times m` covariance matrix

        Notes
        -----
        This is defined as :math:`K(\mathbf{x},\mathbf{x^*})`, where
        :math:`\mathbf{x}` are the given locations and
        :math:`\mathbf{x^*}` are the new sample locations.

        """
        return self.K(self._x, xo)

    def Kxox(self, xo):
        r"""
        Kernel covariance matrix between new sample locations and given
        locations.

        Parameters
        ----------
        xo : numpy.ndarray
            :math:`m` array of new sample locations

        Returns
        -------
        Kxox : numpy.ndarray
            :math:`m\times n` covariance matrix

        Notes
        -----
        This is defined as :math:`K(\mathbf{x^*},\mathbf{x})`, where
        :math:`\mathbf{x^*}` are the new sample locations and
        :math:`\mathbf{x}` are the given locations

        """
        return self.K(xo, self._x)

    def mean(self, xo):
        r"""
        Predictive mean of the gaussian process.

        Parameters
        ----------
        xo : numpy.ndarray
            :math:`m` array of new sample locations

        Returns
        -------
        mean : numpy.ndarray
            :math:`m` array of predictive means

        Notes
        -----
        This is defined by Equation 2.23 of [RW06]_:

        .. math::

            \mathbf{m}(\mathbf{x^*})=K(\mathbf{x^*}, \mathbf{x})\mathbf{K}_{xx}^{-1}\mathbf{y}

        """
        return np.dot(self.Kxox(xo), self.inv_Kxx_y)

    def cov(self, xo):
        r"""
        Predictive covariance of the gaussian process.

        Parameters
        ----------
        xo : numpy.ndarray
            :math:`m` array of new sample locations

        Returns
        -------
        cov : numpy.ndarray
            :math:`m\times m` array of predictive covariances

        Notes
        -----
        This is defined by Eq. 2.24 of [RW06]_:

        .. math::

            \mathbf{C}=K(\mathbf{x^*}, \mathbf{x^*}) - K(\mathbf{x^*}, \mathbf{x})\mathbf{K}_{xx}^{-1}K(\mathbf{x}, \mathbf{x^*})

        """
        Kxoxo = self.Kxoxo(xo)
        Kxox = self.Kxox(xo)
        Kxxo = self.Kxxo(xo)
        return Kxoxo - np.dot(Kxox, np.dot(self.inv_Kxx, Kxxo))

    def dm_dtheta(self, xo):
        r"""
        Derivative of the mean of the gaussian process with respect to
        its parameters, and evaluated at `xo`.

        Parameters
        ----------
        xo : numpy.ndarray
            :math:`m` array of new sample locations

        Returns
        -------
        dm_dtheta : numpy.ndarray
            :math:`n_p\times m` array, where :math:`n_p` is the
            number of parameters (see `params`).

        Notes
        -----
        The analytic form is:

        .. math::

            \frac{\partial}{\partial \theta_i}m(\mathbf{x^*})=\frac{\partial K(\mathbf{x^*}, \mathbf{x})}{\partial \theta_i}\mathbf{K}_{xx}^{-1}\mathbf{y} - K(\mathbf{x^*}, \mathbf{x})\mathbf{K}_{xx}^{-1}\frac{\partial \mathbf{K}_{xx}}{\partial \theta_i}\mathbf{K}_{xx}^{-1}\mathbf{y}

        """

        y = self._y
        Ki = self.inv_Kxx
        Kj = self.Kxx_J
        Kjxo = self.K.jacobian(xo, self._x)
        Kxox = self.Kxox(xo)

        dm = np.empty((len(self.params), xo.size))
        gp_c.dm_dtheta(y, Ki, Kj, Kjxo, Kxox, self._s, dm)

        return dm

    def plot(self, ax=None, xlim=None, color='k', markercolor='r'):
        """
        Plot the predictive mean and variance of the gaussian process.

        Parameters
        ----------
        ax : `matplotlib.pyplot.axes.Axes` (optional)
            The axes on which to draw the graph. Defaults to
            ``plt.gca()`` if not given.
        xlim : (lower x limit, upper x limit) (optional)
            The limits of the x-axis. Defaults to the minimum and
            maximum of `x` if not given.
        color : str (optional)
            The line color to use. The default is 'k' (black).
        markercolor : str (optional)
            The marker color to use. The default is 'r' (red).

        """

        x, y = self._x, self._y

        if ax is None:
            ax = plt.gca()
        if xlim is None:
            xlim = (x.min(), x.max())

        X = np.linspace(xlim[0], xlim[1], 1000)
        mean = self.mean(X)
        cov = self.cov(X)
        std = np.sqrt(np.diag(cov))
        upper = mean + std
        lower = mean - std

        ax.fill_between(X, lower, upper, color=color, alpha=0.3)
        ax.plot(X, mean, lw=2, color=color)
        ax.plot(x, y, 'o', ms=7, color=markercolor)
        ax.set_xlim(*xlim)

    def fit_MLII(self, params_to_fit, bounds=None,
                 randf=None, nrestart=5, verbose=False):
        """
        Fit parameters of the gaussian process using MLII (maximum
        likelihood) estimation.

        Note that this method modifies the gaussian process in
        place. After the method is run, the `GP` object will have new
        parameters set to the best ones found during the optimization.

        The optimization algorithm used is L-BFGS-B.

        Parameters
        ----------
        params_to_fit : boolean array_like
            A list of booleans corresponding to the gaussian process
            parameters, indicating which parameters should be
            fit. Parameters which are not fit keep their current value.

        bounds : list of tuples (optional)
            The upper and lower bounds for each parameter that is being
            fit; use ``None`` to specify no bound. If not specified,
            the bounds default to ``(EPS, None)``, where
            ``EPS=numpy.finfo(float).eps``.

        randf : list of functions (optional)
            A list of functions to give an initial starting value for
            each parameter that is being fit. The functions should
            take no arguments, and return a numpy.float64. If not
            specified, the functions default to ``lambda:
            abs(numpy.random.normal())``.

        nrestart : int (optional)
            Number of random restarts to use. The best parameters out of
            all the random restarts are used.

        verbose : bool (optional)
            Whether to print information about the optimization.

        """

        # original parameter list
        params = list(self.params)
        # boolean array of which parameters to fit
        fitmask = np.array(params_to_fit, dtype='bool')

        # default for bounds
        if bounds is None:
            bounds = tuple((EPS, None) for p in params_to_fit if p)
        # default for randf
        if randf is None:
            randf = tuple(
                lambda: np.abs(np.random.normal())
                for p in params_to_fit if p)

        # figure out the indices of the params we are fitting
        j = 0
        iparam = []
        for i in xrange(len(params)):
            if params_to_fit[i]:
                iparam.append(j)
                j += 1
            else:
                iparam.append(None)

        # update the GP object with new parameter values
        def new_params(theta):
            th = np.array(theta).ravel()
            out = [params[i] if j is None else th[j]
                   for i, j in enumerate(iparam)]
            return out

        # negative log likelihood
        def f(theta):
            self.params = new_params(theta)
            out = -self.log_lh
            return out

        # jacobian of the negative log likelihood
        def df(theta):
            self.params = new_params(theta)
            out = -self.dloglh_dtheta[fitmask]
            return out

        def cb(theta):
            print theta

        # run the optimization a few times to find the best fit
        args = np.empty((nrestart, len(bounds)))
        fval = np.empty(nrestart)
        for i in xrange(nrestart):
            p0 = tuple(r() for r in randf)
            self.params = new_params(p0)
            if verbose:
                print "      p0 = %s" % (p0,)
            popt = optim.minimize(
                fun=f, x0=p0, jac=df, method='L-BFGS-B', bounds=bounds)
            args[i] = popt['x']
            fval[i] = popt['fun']
            if verbose:
                print "      -MLL(%s) = %f" % (args[i], fval[i])

        # choose the parameters that give the best MLL
        if args is None or fval is None:
            raise RuntimeError("Could not find MLII parameter estimates")

        # update our parameters
        self.params = new_params(args[np.argmin(fval)])
