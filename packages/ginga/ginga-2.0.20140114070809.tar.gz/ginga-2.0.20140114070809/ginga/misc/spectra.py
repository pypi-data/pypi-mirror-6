"""
CREDITS: see
  http://nbviewer.ipython.org/urls/raw.github.com/gabraganca/S4/master/notebooks/load-spectrum-FITS.ipynb

"""

import numpy

from ginga.util import wcs

def get_wstart(ref, wave_ref, wave_per_pixel):
    """
    Obtain the starting wavelength of a spectrum.

    Parameters
    ----------

    ref: int,
        Reference pixel.
    
    wave_ref: float,
        Coordinate at reference pixel.

    wave_per_pixel: float,
        Coordinate increase per pixel.

    Returns
    -------

    wstart: float,
        Starting wavelength.

     
    """
    
    return wave_ref - ((ref-1) * wave_per_pixel)


def get_wavelength(start_wave, wave_per_pixel, size):
    """
    Obtain an array of wavelengths according to input values.

    Parameters
    ----------

    start_wave: float,
        Starting wavelength.

    wave_per_pixel: float,
        Wavelength per pixel.

    size: int,
        Size of array.

    Returns
    -------

    wave_array: numpy.ndarray,
        Wavelength array
    """
    
    ## return numpy.array([start_wave + i*wave_per_pixel for i in range(size)],
    ##                    dtype=numpy.float)
    arr = numpy.arange(size, dtype=numpy.float)
    arr *= wave_per_pixel
    arr += start_wave
    return arr
    

def load_spectrum(image):
    """
    Loads the spectrum in FITS format to a numpy.darray.

    Parameters
    ----------

    fname: str,
        File name of the FITS spectrum.

    Returns
    -------

    spectrum: ndarray,
        Spectrum array with wavelength and flux.
    """
    
    # Load spectrum
    flux = image.get_data().flatten()
    
    #Obtain parameters for wavelength determination from header

    #... the wavelength information, along with the spatial information,
    # is usually stored in the fits header entries CDELT1/2/3, CRVAL1/2/3.
    # The first is the dispersion, the second the starting wavelength.
    # There may also be something including "PIX1/2/3", which indicates
    # to which pixel the CRVAL refers (usually 0/1 but sometimes not).
    ref_pixel = image.get_keyword('CRPIX1')
    # Wavelength at reference pixel
    coord_ref_pixel = image.get_keyword('CRVAL1')
    # Wavelength per pixel
    try:
        wave_pixel = image.get_keyword('CDELT1')
    except KeyError:
        wave_pixel = image.get_keyword('CD1_1')
    
    # Get starting wavelength
    wstart = get_wstart(ref_pixel, coord_ref_pixel, abs(wave_pixel))
    print "wavelen start=%f" % (wstart)
    
    # Obtain array of wavelength
    wave = get_wavelength(wstart, wave_pixel, len(flux))
    
    #res = numpy.dstack((wave, flux))[0]
    #return res
    return wave, flux

def plot_spectrum(image, mplfig, plottype='r-', clear=True):

    #res = load_spectrum(image)
    wave, flux = load_spectrum(image)

    # TODO: clear figure
    
    # plot
    ax = mplfig.add_subplot(111)
    ax.set_xlabel('Wavelength')
    ax.set_ylabel('Flux')
    ax.set_title('')
    ax.grid(True)
    #ax.plot(res[:, 0], res[:, 1], plottype)
    ax.plot(wave, flux, plottype)
    return ax


#END


