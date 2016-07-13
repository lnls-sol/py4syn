import sys
import numpy as np

def tvDenoising1D(data, lamb):
    """
    This function implements a 1-D Total Variation denoising according to Condat, L. (2013) "A direct algorithm for 1-D total variation denoising."

    See also: `Condat, L. (2013). A direct algorithm for 1-D total variation denoising. IEEE Signal Processing Letters, 20(11), 1054–1057. doi:10.1109/LSP.2013.2278339 <http://dx.doi.org/10.1109/LSP.2013.2278339>`_

    Parameters
    ----------
    data : array
        Data to be fit
    lamb : float
         .. note::
            **lamb** must be nonnegative. **lamb = 0** will result in **output = data**.

    Returns
    -------
    fitData: `array`


    Examples
    --------
    >>> import pylab as pl
    >>> data = 'testdata.txt'
    >>> X = pl.loadtxt(data);
    >>> x = X[:,0];
    >>> data = X[:,7];
    >>>
    >>> denoised = tvDenoising1D(data, lamb=200)
    >>>
    >>> pl.plot(x, data, 'b')
    >>> pl.hold(True)
    >>> pl.plot(x, denoised, 'r--')
    >>> pl.show()
    """
    N = len(data)

    k = k0 = k_ = kp = 0
    vmin = data[0]-lamb
    vmax = data[0]+lamb
    umin = lamb
    umax = -lamb

    x = np.zeros(len(data))


    while True:
        # 2:
        if(k == N):
            return np.array([vmin+umin])

        # Break condition to avoid overflow...
        if k+1 >= N:
            break

        # 3:
        if(data[k+1]+umin < vmin-lamb):
            for i in range(k0, k_+1):
                x[i] = vmin
            x[k0] = x[k_] = vmin
            k = k0 = k_ = kp = k_+1
            vmin = data[k]
            vmax = data[k]+(2*lamb)
            umin = lamb
            umax = -lamb
        # 4:
        elif(data[k+1]+umax > vmax+lamb):
            for i in range(k0, kp+1):
                x[i] = vmax
            x[k0] = x[k_] = x[kp] = vmax
            k = k0 = k_ = kp = kp+1
            vmin = data[k]-(2*lamb)
            vmax = data[k]
            umin = lamb
            umax = -lamb
        # 5:
        else:
            k = k+1
            umin = umin +data[k] - vmin
            umax = umax + data[k] - vmax
            # 6:
            if(umin >= lamb):
                vmin = vmin + ((umin -lamb)/(k-k0+1))
                umin = lamb
                k_ = k
            if(umax <= -lamb):
                vmax = vmax+((umax + lamb)/(k-k0+1))
                umax = -lamb
                kp = k
        # 7:
        if k < N:
            continue

        # 8:
        if(umin < 0):
            for i in range(k0, k_+1):
                x[i] = vmin
            k = k0 = k_ = k_ + 1
            vmin = data[k]
            umin = lamb
            umax = data[k] + lamb - vmax
            continue
        # 9:
        elif(umax > 0):
            for i in range(k0, kp+1):
                x[i] = vmax
            k = k0 = kp = kp+1
            vmax = data[k]
            umax = -lamb
            umin = data[k]-lamb-vmin
            continue
        else:
            for i in range(k0, N):
                x[i] = vmin+(umin/(k-k0+1))
            break

    return x


def fitGauss(xarray, yarray):
    """
    This function mix a Linear Model with a Gaussian Model (LMFit).

    See also: `Lmfit Documentation <http://cars9.uchicago.edu/software/python/lmfit/>`_

    Parameters
    ----------
    xarray : array
        X data
    yarray : array
        Y data

    Returns
    -------
    peak value: `float`
    peak position: `float`
    min value: `float`
    min position: `float`
    fwhm: `float`
    fwhm positon: `float`
    center of mass: `float`
    fit_Y: `array`
    fit_result: `ModelFit`


    Examples
    --------
    >>> import pylab as pl
    >>> data = 'testdata.txt'
    >>> X = pl.loadtxt(data);
    >>> x = X[:,0];
    >>> y = X[:,7];
    >>>
    >>> pkv, pkp, minv, minp, fwhm, fwhmp, com = fitGauss(x, y)
    >>> print("Peak ", pkv, " at ", pkp)
    >>> print("Min ", minv, " at ", minp)
    >>> print("Fwhm ", fwhm, " at ", fwhmp)
    >>> print("COM = ", com)
    >>>
    """
    from lmfit.models import GaussianModel, LinearModel

    y = yarray
    x = xarray

    gaussMod = GaussianModel()
    linMod = LinearModel()
    pars = linMod.make_params(intercept=y.min(), slope=0)
    pars += linMod.guess(y, x=x)

    pars += gaussMod.guess(y, x=x)

    mod = gaussMod + linMod

    fwhm = 0
    fwhm_position = 0

    try:
        result = mod.fit(y, pars, x=x)
        fwhm = result.values['fwhm']
        fwhm_position = result.values['center']
    except:

        result = None


    peak_position = xarray[np.argmax(y)]
    peak = np.max(y)

    minv_position = x[np.argmin(y)]
    minv = np.min(y)

    COM = (np.multiply(x,y).sum())/y.sum()

    return (peak, peak_position, minv, minv_position, fwhm, fwhm_position, COM, result)

if __name__ == '__main__':
    import pylab as pl

    #file = '/home/ABTLUS/hugo.slepicka/devfiles/workspacePython/FIT_Test/teste'
    file = "/home/ABTLUS/hugo.slepicka/SVN/Py4Syn/trunk/lab6_summed.dat"
    X = np.loadtxt(file);
    x = X[:,0];
    y = X[:,1];

    #x = np.asarray([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    #y = np.asarray([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

    #peak, peak_position, minv, minv_position, fwhm, fwhm_position, COM, result = fitGauss(x, y)
    #print("COM = ", result)
    data = y
    denoised = tvDenoising1D(data, lamb=200)

    pl.plot(x, data, 'b')
    pl.hold(True)
    pl.plot(x, denoised, 'r--')
    pl.show()
