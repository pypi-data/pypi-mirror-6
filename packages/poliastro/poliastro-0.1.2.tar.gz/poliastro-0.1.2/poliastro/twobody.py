"""Two-body dynamics.

"""

import numpy as np

from .util import rotate
from . import _ast2body

__all__ = ['coe2rv', 'rv2coe', 'kepler']


def coe2rv(k, a, ecc, inc, omega, argp, nu,
           arglat=None, truelon=None, lonper=None):
    """Converts classical orbital elements to r, v IJK vectors.

    Parameters
    ----------
    k : float
        Standard gravitational parameter (km^3 / s^2).
    a : float
        Semi-major axis (km).
    ecc : float
        Eccentricity.
    inc : float
        Inclination (rad).
    omega : float
        Longitude of ascending node (rad).
    argp : float
        Argument of perigee (rad).
    nu : float
        True anomaly (rad).
    arglat : float (optional)
        Argument of latitude (rad), default to None.
    truelon : float (optional)
        True longitude (rad), default to None.
    lonper : float (optional)
        Longitude of periapsis (rad), default to None.

    Examples
    --------
    From Vallado 2007, ex. 2-6
    >>> p = 11067.790
    >>> ecc = 0.83285
    >>> a = p / (1 - ecc ** 2)
    >>> coe2rv(3.986e5, a, 0.83285, np.radians(87.87),
    ... np.radians(227.89), np.radians(53.38), np.radians(92.335))
    (array([ 6525.36812099,  6861.5318349 ,  6449.11861416]),
    array([ 4.90227593,  5.5331365 , -1.975709  ]))

    """
    # TODO: Include special cases with extra arguments
    p = a * (1 - ecc ** 2)
    r_pqw = np.array([
        p * np.cos(nu) / (1 + ecc * np.cos(nu)),
        p * np.sin(nu) / (1 + ecc * np.cos(nu)),
        0
    ])
    v_pqw = np.array([
        -np.sqrt(k / p) * np.sin(nu),
        np.sqrt(k / p) * (ecc + np.cos(nu)),
        0
    ])
    r_ijk = rotate(r_pqw, 3, -argp)
    r_ijk = rotate(r_ijk, 1, -inc)
    r_ijk = rotate(r_ijk, 3, -omega)

    v_ijk = rotate(v_pqw, 3, -argp)
    v_ijk = rotate(v_ijk, 1, -inc)
    v_ijk = rotate(v_ijk, 3, -omega)

    return r_ijk, v_ijk


def rv2coe(k, r, v):
    """Converts r, v to classical orbital elements.

    This is a wrapper around rv2coe from ast2body.for.

    Parameters
    ----------
    k : float
        Standard gravitational parameter (km^3 / s^2).
    r : array
        Position vector (km).
    v : array
        Velocity vector (km / s).

    Examples
    --------
    Vallado 2001, example 2-5
    >>> r = [6524.834, 6862.875, 6448.296]
    >>> v = [4.901327, 5.533756, -1.976341]
    >>> k = 3.986e5
    >>> rv2coe(k, r, v)
    (36127.55012131963, 0.83285427644495158, 1.5336055626394494,
    3.9775750028016947, 0.93174413995595795, 1.6115511711293014)

    """
    # TODO: Extend for additional arguments arglat, truelon, lonper
    r = np.asanyarray(r).astype(np.float)
    v = np.asanyarray(v).astype(np.float)
    _, a, ecc, inc, omega, argp, nu, _ = _ast2body.rv2coe(r, v, k)
    return a, ecc, inc, omega, argp, nu


def kepler(k, r0, v0, tof):
    """Propagates orbit.

    This is a wrapper around kepler from ast2body.for.

    Parameters
    ----------
    k : float
        Gravitational constant of main attractor (km^3 / s^2).
    r0 : array
        Initial position (km).
    v0 : array
        Initial velocity (km).
    tof : float
        Time of flight (s).

    Raises
    ------
    RuntimeError
        If the status of the subroutine is not 'ok'.

    """
    r0 = np.asanyarray(r0).astype(np.float)
    v0 = np.asanyarray(v0).astype(np.float)
    tof = float(tof)
    assert r0.shape == (3,)
    assert v0.shape == (3,)
    r, v, error = _ast2body.kepler(r0, v0, tof, k)
    error = error.strip().decode('ascii')
    if error != 'ok':
        raise RuntimeError("There was an error: {}".format(error))
    return r, v
