# Tests for FFT based propagation

from .. import poppy_core as poppy
import numpy as np
import astropy.io.fits as fits
from .test_core import check_wavefront

wavelen = 1e-6 
radius = 6.5/2


def test_fft_normalization():
    """ Test the PSF normalization for FFTs"""

    osys = poppy.OpticalSystem("test", oversample=2)
    osys.addPupil(function='Circle', radius=radius)
    osys.addImage() # null plane to force FFT
    osys.addPupil() # null plane to force FFT
    osys.addDetector(pixelscale=0.01, fov_arcsec=10.0) # use a large FOV so we grab essentially all the ligh        

    # Expected value here is 0.9977
    psf = osys.calcPSF(wavelength=2.0e-6, normalize='first')
    assert abs(psf[0].data.sum() - 0.9977) < 0.001


def test_fft_blc_coronagraph():
    """ Test that a simple band limited coronagraph blocks most of the light """

    lyot_radius = 6.5/2.5
    osys = poppy.OpticalSystem("test", oversample=2)
    osys.addPupil('Circle', radius=radius)
    osys.addImage()
    osys.addImage('BandLimitedCoron', kind='circular', sigma=5.0)
    osys.addPupil()
    osys.addPupil('Circle', radius=lyot_radius)
    osys.addDetector(pixelscale=0.10, fov_arcsec=5.0)

    psf, int_wfs = osys.calcPSF(wavelength=wavelen, display_intermediates=False, return_intermediates=True)


    # after the Lyot plane, the wavefront should be all real.
    lyot_wf = int_wfs[-2]
    lyot_wf_fits = lyot_wf.asFITS(what='all') # need to save this for the multiwave comparison in test_3_multiwave()
    assert check_wavefront(lyot_wf_fits, test='is_real', comment='(Lyot Plane)')

    # and the flux should be low.
    assert psf[0].data.sum() < 1e-4



def test_fft_fqpm(): #oversample=2, verbose=True, wavelength=2e-6):
    """ Test FQPM plus field mask together. The check is that there should be very low flux in the final image plane 
    Perfect circular case  with FQPM with fieldMask
    Test  ideal FQPM, with field mask. Verify proper behavior in Lyot plane"""


    oversamp=2
    osys = poppy.OpticalSystem("test", oversample=oversamp)
    osys.addPupil('Circle', radius=radius)
    osys.addPupil('FQPM_FFT_aligner')
    osys.addImage('FQPM', wavelength=wavelen)  # perfect FQPM for this wavelength
    osys.addImage('fieldstop', size=6.0)
    osys.addPupil('FQPM_FFT_aligner', direction='backward')
    osys.addPupil('Circle', radius=radius)
    osys.addDetector(pixelscale=0.01, fov_arcsec=10.0)

    psf = osys.calcPSF(wavelength=wavelen, oversample=oversamp)
    assert psf[0].data.sum() <  0.002
    #_log.info("post-FQPM flux is appropriately low.")



def test_SAMC():
    """ Test semianalytic coronagraphic method

    """
    lyot_radius = 6.5/2.5
    pixelscale = 0.010

    osys = poppy.OpticalSystem("test", oversample=4)
    osys.addPupil('Circle', radius=radius, name='Entrance Pupil')
    osys.addImage('CircularOcculter', radius = 0.1)
    osys.addPupil('Circle', radius=lyot_radius, name = "Lyot Pupil")
    osys.addDetector(pixelscale=pixelscale, fov_arcsec=5.0)


    #plt.figure(1)
    sam_osys = poppy.SemiAnalyticCoronagraph(osys, oversample=8, occulter_box=0.15)

    #t0s = time.time()
    psf_sam = sam_osys.calcPSF()
    #t1s = time.time()

    #plt.figure(2)
    #t0f = time.time()
    psf_fft = osys.calcPSF()
    #t1f = time.time()

    #plt.figure(3)
    #plt.clf()
    #plt.subplot(121)
    #poppy.utils.display_PSF(psf_fft, title="FFT")
    #plt.subplot(122)
    #poppy.utils.display_PSF(psf_sam, title="SAM")


    
    maxdiff = np.abs(psf_fft[0].data - psf_sam[0].data).max()
    #print "Max difference between results: ", maxdiff

    assert( maxdiff < 1e-7)



# TODO: Add a function that uses both the DFT and MFT for the exact same calc, and compare the results
