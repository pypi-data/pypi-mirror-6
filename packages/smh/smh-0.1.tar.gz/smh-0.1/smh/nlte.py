# coding: utf-8

""" Contains code to calculate non-LTE corrections """

__author__ = "Andy Casey <andy@astrowizici.st>"

# Third party imports
import numpy as np
from scipy.io import readsav

__all__ = ["get_nlte_correction"]

def find_range(data, value):
    """ Returns the range values for a value in a given data array """

    data = np.array(data)
    if np.any(data == value):
        index = np.where(data == value)[0][0]
        return np.array([index, index + 1])

    if not (np.max(data) >= value >= np.min(data)):
        return np.nan

    distance = data - value
    neighbours = np.array([
        np.where(distance < 0)[0][-1],
        np.where(distance > 0)[0][0] + 1
        ])
    return neighbours


def get_nlte_correction(grid, rest_wavelength, equivalent_width, teff,
    logg, feh, xi, solar_fe_abundance=7.45, verbose=True):
    """ Calculate the non-local thermal equilibrium correction for the
    provided correction grid under the plasma conditions.

    Inputs
    ------
    grid : str or dict
        The filename for the grid of pre-computed non-LTE corrections
        to use, or the loaded grid itself.

    rest_wavelength : float
        The rest wavelength of the line to make the correction for.

    equivalent_width : float
        The measured equivalent width in milliAngstroms (10^-13 m)

    teff : float
        The effective temperature of the star (Kelvin)

    logg : float
        The effective surface gravity of the star (cm/s^2)

    feh : float
        The overall metallicity ([Fe/H]) of the star.

    xi : float
        Microturbulence of the stellar atmosphere (km/s)
    """

    if isinstance(grid, str):
        grid = readsav(grid)

    # Convert equivalent width from milliAngstroms to picometers
    equivalent_width *= 0.1

    # Convert rest wavelength from Angstroms to nanometers
    rest_wavelength /= 10.

    # Check equivalent width
    if not (100 >= equivalent_width >= 0.1):
        raise ValueError("equivalent width was outside of range")
        
    # Check rest wavelength (wv -> wavelength)
    if not np.less_equal(np.abs(grid["wv"] - rest_wavelength), 1e-6).any():
        raise ValueError("atomic transition not found -- wavelengths must match to 6 digits")
        
    # Check temperature (tg -> temperature)
    if not (grid["tg"].max() >= teff >= grid["tg"].min()):
        raise ValueError("temperature outside of range")
        
    # Check surface gravity (gg -> surface gravity)
    if not (grid["gg"].max() >= logg >= grid["gg"].min()):
        raise ValueError("surface gravity outside of range")
        
    # Check microturbulence (xg -> microturbulence)
    if not (grid["xg"].max() >= xi >= grid["xg"].min()):
        raise ValueError("microturbulence outside of range")
        
    # Check metallicity (fg -> metallicity)
    if not (grid["fg"].max() >= feh >= grid["fg"].min()):
        raise ValueError("metallicity outside of range")
        
    # Check for sensible stellar parameters
    if teff > 6500 and 3 > logg:
        raise ValueError("non-sensical stellar parameters: minimum logg = 3 for Teff > 6500 K")
    if teff > 5500 and 2 > logg:
        raise ValueError("non-sensical stellar parameters: minimum logg = 2 for Teff > 5500 K")
    if xi > 2 and logg > 3:
        raise ValueError("non-sensical stellar parameters: maximum xi = 2 km/s for logg > 3")

    # Get indices
    i_teff = find_range(grid["tg"], teff)
    i_logg = find_range(grid["gg"], logg)
    i_xi = find_range(grid["xg"], xi)
    
    i_wavelength = np.where(grid["wv"] == rest_wavelength)[0][0]
    
    nr = len(grid["fg"])
    sl = grid["wl"][
        i_wavelength,           
        i_xi[0]:i_xi[1],        
        :,                      
        i_logg[0]:i_logg[1],    
        i_teff[0]:i_teff[1]     
        ]
    sn = grid["wn"][
        i_wavelength,
        i_xi[0]:i_xi[1],        
        :,                      
        i_logg[0]:i_logg[1],    
        i_teff[0]:i_teff[1]     
        ]

    # Ensure the correct shape
    for axis, indices in zip((0, 2, 3), (i_xi, i_logg, i_teff)):
        if np.ptp(indices) == 1:
            sl = np.concatenate((sl, sl), axis=axis)
            sn = np.concatenate((sn, sn), axis=axis)

    if sn.max() == -9 and sl.max() == -9:
        raise ValueError("model missing from grid or not enough data points")

    # Exclude -9 entries
    remove_indices = []
    for i in xrange(nr):
        if (sl[:, i, :, :].min() == -9) or (sn[:, i, :, :].min() == -9):
            remove_indices.append(i)

    # Do we have enough *valid* points still?
    nr -= len(remove_indices)
    if 2 > nr:
        raise ValueError("model missing from grid or not enough data points")

    # Update the arrays
    sl = np.delete(sl, remove_indices, axis=1)
    sn = np.delete(sn, remove_indices, axis=1)
    grid_fehs = np.delete(grid["fg"], remove_indices, axis=0)

    # Check metallicity to make sure we're still in a valid range
    if not (grid_fehs.max() >= feh >= grid_fehs.min()):
        raise ValueError("metallicity outside of range")
    
    i_feh = find_range(grid_fehs, feh)

    # Interpolate in effective temperature
    tl = np.zeros((2, nr, 2))
    tn = np.zeros((2, nr, 2))
    l = 0 if (i_teff[0] == i_teff[1]) else (teff - grid["tg"][i_teff[0]]) / (grid["tg"][i_teff[1]] - grid["tg"][i_teff[0]])
    
    for k in xrange(2):
        for m in xrange(2):
            tl[m, :, k] = sl[m, :, k, 0] + l * (sl[m, :, k, 1] - sl[m, :, k, 0])
            tn[m, :, k] = sn[m, :, k, 0] + l * (sn[m, :, k, 1] - sn[m, :, k, 0])

    # Interpolate in surface gravity
    gl = np.zeros((2, nr))
    gn = np.zeros((2, nr))
    l = 0 if (i_logg[0] == i_logg[1]) else (logg - grid["gg"][i_logg[0]]) / (grid["gg"][i_logg[1]] - grid["gg"][i_logg[0]])
    for m in xrange(2):
        gl[m, :] = tl[m, :, 0] + l * (tl[m, :, 1] - tl[m, :, 0])
        gn[m, :] = tn[m, :, 0] + l * (tn[m, :, 1] - tn[m, :, 0])

    # Interpolate in microturbulence
    l = 0 if (i_xi[0] == i_xi[1]) else (xi - grid["xg"][i_xi[0]]) / (grid["xg"][i_xi[1]] - grid["xg"][i_xi[0]])
    xl = gl[0, :] + l * (gl[1, :] - gl[0, :])
    xn = gn[0, :] + l * (gn[1, :] - gn[0, :])

    # Scale the metallicities properly
    feh += solar_fe_abundance
    grid_fehs += solar_fe_abundance

    # Check equivalent width
    log_ew = np.log10(equivalent_width)
    if not (xl.max() >= log_ew >= xl.min()):
        raise ValueError("Equivalent widths outside range of LTE curve-of-growth")

    if not (xn.max() >= log_ew >= xn.min()):
        raise ValueError("Equivalent width outside range of non-LTE curve-of-growth")

    # Find LTE abundance from LTE curve-of-growth
    i_lte = np.searchsorted(xl, log_ew) + [0, 1]
    l = 0 if (i_lte[0] == i_lte[1]) else (log_ew - xl[i_lte[0]]) / (xl[i_lte[1]] - xl[i_lte[0]])
    lte_abundance = grid_fehs[i_lte[0]] + l * (grid_fehs[i_lte[1]] - grid_fehs[i_lte[0]])

    # Find non-LTE abundance from non-LTE curve-of-growth
    i_nlte = np.searchsorted(xn, log_ew) + [0, 1]
    l = 0 if (i_nlte[0] == i_nlte[1]) else (log_ew - xn[i_nlte[0]]) / (xn[i_nlte[1]] - xn[i_nlte[0]])
    nlte_abundance = grid_fehs[i_nlte[0]] + l * (grid_fehs[i_nlte[1]] - grid_fehs[i_nlte[0]])

    # Replace abundances that are -9's with np.nans
    if lte_abundance == -9: lte_abundance = np.nan
    if nlte_abundance == -9: nlte_abundance = np.nan
    correction = nlte_abundance - lte_abundance

    return (lte_abundance, nlte_abundance, correction)

