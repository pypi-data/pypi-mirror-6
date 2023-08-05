from __future__ import print_function, division

# Still to implement:
# - Performance monitoring
# - Remove resolved models
# - Optional FITS input/output
# - Output convolved fluxes

try:
    import cPickle as pickle
except ImportError:
    import pickle

import numpy as np
from astropy import units as u

from . import timer

from .models import Models
from .fit_info import FitInfo
from .source import Source
from .utils import io
from .utils.validator import validate_scalar, validate_array
from . import six


def fit(data, filter_names, apertures, model_dir, output, n_data_min=3,
        extinction_law=None, av_range=None, distance_range=None,
        output_format=('F', 6.), output_convolved=False,
        remove_resolved=False):
    """
    Fit a set of sources with models

    Parameters
    ----------
    data : str
        Filename of the file containing the data, one source per line (see
        documentation for a description of the required format).
    filter_names : tuple or list
        List of filter names (given as individual strings) for which the data
        is defined. The filter names should be the name of the files in the
        ``convolved`` directory for the models, without the extensions. This is
        typically ``2J``, ``I1``, ``M1``, etc.
    apertures : :class`~astropy.units.quantity.Quantity` array instance
        The aperture radii that the data is specified in (as an angle). The
        fluxes may not be measured from aperture photometry, but this is meant
        to give an indication of the sizescale of the emission, and can be used
        to reject models that would have been clearly resolved at the distance
        specified.
    models_dir : str
        Name of the directory containing the models to use.
    output : str
        Name of the file to output the fit information to (in binary format).
    extinction_law : :class:`~sedfitter.extinction.Extinction` instance
        The extinction law to use.
    av_range : tuple
        Minimum and maximum Av to allow in the fitting.
    distance_range : :class`~astropy.units.quantity.Quantity` array instance
        Minimum and maximum distance to allow in the fitting in units of length.
    n_data_min : int, optional
        The minimum number of points a source needs to be fit.
    output_format : tuple, optional
        Tuple specifying which fits should be output. See the documentation
        for a description of the tuple syntax.
    output_convolved : bool, optional
        Whether to output the convolved fluxes (necessary if the convolved
        model fluxes are needed for the SED plot).
    remove_resolved : bool, optional
        If set, then models larger than the aperture are removed. See
        Robitaille et al. (2007) for a discussion of this criterion.
    """

    validate_array('apertures', apertures, domain='positive', ndim=1, physical_type='angle')
    validate_array('distance_range', distance_range, domain='positive', ndim=1, shape=(2,), physical_type='length')

    print(" ------------------------------------------------------------")
    print("  => Fitting parameters")
    print(" ------------------------------------------------------------")
    print("")
    print("   Minimum A_V      : %9.3f mag" % av_range[0])
    print("   Maximum A_V      : %9.3f mag" % av_range[1])
    print("   Minimum distance : %9.3f %s" % (distance_range[0].value, distance_range.unit))
    print("   Maximum distance : %9.3f %s" % (distance_range[1].value, distance_range.unit))
    print("")
    print(" ------------------------------------------------------------")
    print("  => Output parameters")
    print(" ------------------------------------------------------------")
    print("")
    print("   File   : %s" % output)
    print("   Format : %s" % output_format[0])
    print("   Number : %g" % output_format[1])
    print("")
    print(" ------------------------------------------------------------")
    print("  => Data format parameters")
    print(" ------------------------------------------------------------")
    print("")
    print("   Number of filters :  %i" % len(filter_names))
    print("")

    # Open datafile
    if isinstance(data, six.string_types):
        data_file = open(data, 'r')
    else:
        data_file = data

    if len(apertures) != len(filter_names):
        raise ValueError("length of apertures list should match length of filter names list")

    # Construct filters dictionary
    filters = []
    for i in range(len(apertures)):
        filters.append({'aperture_arcsec': apertures[i].to(u.arcsec).value, 'name': filter_names[i]})

    # Read in models
    models = Models.read(model_dir, filters, distance_range=distance_range, remove_resolved=remove_resolved)

    # Add wavelength to filters
    for i, f in enumerate(filters):
        f['wav'] = models.wavelengths[i]

    print('')
    print('     Filter    Wavelength    Aperture (")   ')
    print('    ----------------------------------------')
    for f in filters:
        print('       %5s   %9.2f  %9.2f        ' % (f['name'], f['wav'].to(u.micron).value, f['aperture_arcsec']))
    print('')

    # Set Av law
    av_law = extinction_law.get_av(models.wavelengths)

    # Set scale model - make this a scalar
    sc_law = -2. * np.ones(av_law.shape)

    # Cycle through sources

    io.delete_file(output)

    fout = open(output, 'wb')
    pickle.dump(model_dir, fout, 2)
    pickle.dump(filters, fout, 2)
    pickle.dump(extinction_law, fout, 2)

    # NOTE _ CAN USE PROTOCOL 2 IN SOURCE FOR COORINDATES

    s = Source()

    t = timer.Timer()

    while True:

        try:
            s = Source.from_ascii(data_file.readline())
        except EOFError:
            break

        if s.n_data >= n_data_min:

            info = FitInfo(source=s)
            info.av, info.sc, info.chi2, info.model_name, model_fluxes = models.fit(s, av_law, sc_law, av_range[0], av_range[1])

            if output_convolved:
                info.model_fluxes = model_fluxes

            info.sort()
            info.keep(output_format[0], output_format[1])

            pickle.dump(info, fout, 2)

            t.display()

    t.display(force=True)

    fout.close()
