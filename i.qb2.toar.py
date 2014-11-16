# -*- coding: utf-8 -*-
"""
AUTHOR:         Nikos Alexandris | Trikala, November 2014 00:47:30 2014
                Converted from a bash shell script
"""

#%Module
#%  description: Converting QuickBird2 (radiometrically corrected) digital numbers to Top-of-Atmosphere Spectral Radiance or Reflectance  (Krause, 2005)
#%  keywords: imagery, radiometric conversion, radiance, reflectance, QuickBird2
#%End

#%flag
#%  key: r
#%  description: Convert to at-sensor spectral radiance
#%end

#%flag
#%  key: k
#%  description: Keep current computational region settings
#%end

#%option G_OPT_R_INPUTS
#% key: band
#% key_desc: band name
#% type: string
#% label: QuickBird2 band
#% description: QuickBird2 acquired spectral band(s) (DN values)
#% multiple: yes
#% required: yes
#%end

#%option G_OPT_R_BASENAME_OUTPUT
#% key: outputsuffix
#% key_desc: suffix string
#% type: string
#% label: output file(s) suffix
#% description: Suffix for spectral radiance or reflectance output image(s)
#% required: yes
#% answer: toar
#%end

#%option
#% key: utc
#% key_desc: YYYY_MM_DDThh:mm:ss:ddddddZ;
#% type: string
#% label: UTC
#% description: Coordinated Universal Time string as identified in the acquisition's metadata file (.IMD)
#% guisection: Metadata
#% required: yes
#%end

#%option
#% key: doy
#% key_desc: day of year
#% type: integer
#% label: Day of Year
#% description: User defined aquisition's Day of Year (Julian Day) to calculate Earth-Sun distance
#% options: 1-365
#% guisection: Metadata
#% required: no
#%end

#%option
#% key: sea
#% key_desc: degrees
#% type: double
#% label: Sun Elevation Angle
#% description: Aquisition's mean sun elevation angle
#% options: 0.0 - 90.0
#% guisection: Metadata
#% required: yes
#%end

#%option
#% key: tdi
#% key_desc: integer
#% type: integer
#% label: TDI level
#% description: TDI-based (time delayed integration) exposure level of the Panchromatic band
#% options: 10;13;18;24;32
#% guisection: Metadata
#% required: yes
#%end

# required librairies -------------------------------------------------------
import math


# globals


# constants
from quickbird2 import Esun, KCF
spectral_bands = KCF.keys()


# string for metadata
source1_rad = source1_toar = '"Radiometric Use of QuickBird Imagery, '
'Technical Note (2005)," by Keith Krause, Digital Globe'
source2_rad = source2_toar = ""  # Add some source2?


# Aquisition's MetaData -----------------------------------------------------

#?

# helper functions ----------------------------------------------------------
def cleanup():
    grass.run_command('g.remove', flags='f', type="rast",
                      pattern='tmp.%s*' % os.getpid(), quiet=True)


def run(cmd, **kwargs):
    """ """
    grass.run_command(cmd, quiet=True, **kwargs)


def main():

    global acq_time, esd

    """1st, get input, output, options and flags"""

    spectral_bands = options['band'].split(',')
    outputsuffix = options['outputsuffix']
    utc = options['utc']
    doy = options['doy']
    sea = options['sea']
    tdi = options['tdi']
    radiance = flags['r']
    keep_region = flags['k']

    # -----------------------------------------------------------------------
    # List images and their properties
    # -----------------------------------------------------------------------

    mapset = grass.gisenv()['MAPSET']  # Current Mapset?

#    imglst = [pan]
#    imglst.extend(msxlst)  # List of input imagery

    images = {}
    for img in spectral_bands:  # Retrieving Image Info
        images[img] = Info(img, mapset)
        images[img].read()

    # -----------------------------------------------------------------------
    # Temporary Region and Files
    # -----------------------------------------------------------------------

    if not keep_region:
        grass.use_temp_region()  # to safely modify the region
    tmpfile = grass.tempfile()  # Temporary file - replace with os.getpid?
    tmp = "tmp." + grass.basename(tmpfile)  # use its basename

    # -----------------------------------------------------------------------
    # Global Metadata: Earth-Sun distance, Sun Zenith Angle
    # -----------------------------------------------------------------------

    acq_utc = AcquisitionTime(utc)  # will hold esd (earth-sun distance)
    acq_dat = datetime(acq_utc.year, acq_utc.month, acq_utc.day)

    # Earth-Sun distance
    if doy:
        esd = jd_to_esd(int(doy))

    elif utc:
        esd = acq_utc.esd

    else:
        grass.fatal(_("Either the UTC string or "
                      "the Day-of-Year (doy) are required!"))

    sza = 90 - float(sea)  # Sun Zenith Angle based on Sun Elevation Angle

    # -----------------------------------------------------------------------
    # Loop processing over all bands
    # -----------------------------------------------------------------------
    for band in spectral_bands:

#        # Why is this necessary?  Any function to remove the mapsets name?
#        if '@' in band:
#            band_key = (band.split('@')[0])
#        else:
#            band_key = band

        # -------------------------------------------------------------------
        # Band dependent metadata for Spectral Radiance
        # -------------------------------------------------------------------

        # which Pan TDI level?
        if band == 'Pan':
            band_key = band + tdi
            g.message("Processing for %s" % pantdi)

        # some echo...
        g.message("Processing the %s spectral band" % band)
    
        # check bitness
        if 0 <= images[band].max() <= 255:
            # 8-bit
            kcf = float(KFC[band_key][1])
        else:
            # 16-bit
            kcf = float(KFC[band_key][2])

        # effective bandwidth        
        bw = float(KFC[band_key][0])


        # -------------------------------------------------------------------
        # Converting to Spectral Radiance
        # -------------------------------------------------------------------

        # inform
        msg ="Band Parameters set to K=%f, Bandwidth=%.1f" % (kcf, bw)
        g.message(msg)

         # set region
        run('g.region', rast=band)   # ## FixMe?
        msg = "Region matching the %s spectral band" % band

        # conversion to Radiance based on (1) 
        msg = "Radiance = K * DN / Bandwidth"
        g.message(msg)

        rad = "%s = %f * %d / %f" \
            % (tmp_rad, kcf, dn, bw)  # Attention: 32-bit calculations required
        grass.mapcalc(rad)
        
        # for tmp_rad -- MOVE below
        title_rad=""
        description_rad="Top-of-Atmosphere %s band spectral Radiance [W/m^2/sr/μm]" % band
        units_rad="W / sq.m. / μm / ster"

        if not radiance:

            # ---------------------------------------------------------------
            # Converting to Top-of-Atmosphere Reflectance
            # ---------------------------------------------------------------

            global tmp_toar
            
            esun = float(QB2ESUN[band_key])
            msg = "Using Esun = %f" % esun
            g.message(msg)
    
            # calculate ToAR  -- tmp_rad is already 32-bit -- see above!
            msg = "Reflectance = ( π * Radiance * ESD^2 ) / BAND_Esun * cos(SZA)"
            g.message(msg)
    
            toar = "%s = math.pi * %s * %f^2 / %f * %f" \
                % (tmp_toar, tmp_rad, esd, esun, sza)
            grass.mapcalc(toar)

            # for tmp_toar -- MOVE below!
            title_toar="echo ${BAND} band (Top of Atmosphere Reflectance)"
            description_toar="Top of Atmosphere %s band spectral Reflectance" % band
            units_toar="Unitless planetary reflectance"
            history_toar="K=%f; Bandwidth=%.1f; ESD=%f; Esun=%f; SZA=%.1f" % (kcf, bw, esd, esun, sza)

    if tmp_toar:

        # history entry
        run("r.support", map=tmp_toar,
            title=title_toar, units=units_toar, description=description_toar,
            source1=source1_toar, source2=source2_toar, history=history_toar)

        # add suffix to basename & rename end product
#        toar_name = ("%s.%s" % (band, outputsuffix))
        toar_name = ("%s.%s" % (band.split('@')[0], outputsuffix))
        run("g.rename", rast=(tmp_toar, toar_name))

    elif tmp_rad:

        # history entry
        run("r.support", map=tmp_rad,
            title=title_rad, units=units_rad, description=description_rad,
            source1=source1_rad, source2=source2_rad, history=history_rad)

        # add suffix to basename & rename end product        
#        rad_name = ("%s.%s" % (band, outputsuffix))
        rad_name = ("%s.%s" % (band.split('@')[0], outputsuffix))
        run("g.rename", rast=(tmp_rad, rad_name))