# -*- coding: utf-8 -*-
"""
@author: nik | Created on Wed Nov 12 00:47:30 2014
"""

import math


def cleanup():
    grass.run_command('g.remove', flags='f', type="rast",
                      pattern='tmp.%s*' % os.getpid(), quiet=True)


def run(cmd, **kwargs):
    """ """
    grass.run_command(cmd, quiet=True, **kwargs)


# Constants
math.pi  # PI=3.14159265358

# Aquisition MetaData -- Hardcoded!

# Acquisition's Day of Year and estimated Earth-Sun Distance
DOY=274
ESD=1.001190 # depends on DOY, get from xls file?

# Sun Zenith Angle based on the acquisition's Sun Elevation Angle
SEA = 67.8
SZA = 90 - SEA

# which Pan time-delayed integration (TDI) level?
tdi = "10"  # get from metadata






###
# Bands
spectral_bands=['Pan', 'Blue', 'Green', 'Red', 'NIR']
 
 
# loop over bands
for band in spectral_bands:
 
    # which Pan TDI level?
    if band == 'Pan':
        pantdi = band + tdi
        print pantdi
        
        
        eval Pan="Pan${PanTDI}"


        g.message("Processing for %s" % pantdi)


        eval BAND="${Pan}"

 
  # some echo...
  echo "Processing the ${BAND} spectral band"
 
  # set band parameters as variables  -- using  K16  for 16-bit data!
  eval K_BAND="K16_${BAND}"
  eval BAND_Width="${BAND}_Width"
  echo "Band Parameters set to K=${!K_BAND}, Bandwidth=${!BAND_Width}"
 
  if [[ ${BAND} == Pan* ]]
  then
    BAND="Pan" ; echo "Processing the ${BAND} spectral band"
  fi
 
     # set region
     # g.region rast=${BAND}_DNs #-pg
     # echo "Region matching the ${BAND} spectral band"
 
#     ?

    # conversion to Radiance based on (1) -- attention: 32-bit calculations required
    #r.mapcalc "${BAND}_Radiance = ( double(${!K_BAND}) * ${BAND}_DNs ) / ${!BAND_Width}"
    #r.info -r "${BAND}_Radiance"
 
    msg = "Radiance = K * DN / Bandwidth"
    g.message(msg)
    rad = "%s = %f * %d / %f" \
    % (rad, kcf, dn, bw)
    grass.mapcalc(rad)
    
    # add info
    #  r.support map=${BAND}_Radiance \
    #  title="" \
    #  units="W / sq.m. / μm / ster" \
    #  description="Top-of-Atmosphere `echo ${BAND}` band spectral Radiance [W/m^2/sr/μm]" \
    #  source1='"Radiometric Use of QuickBird Imagery, Technical Note (2005)," by Keith Krause, Digital Globe'



    eval BAND_Esun="${BAND}_Esun"  # This needs conversion to Python!
    msg = "Using Esun = %f" % esun
    g.message(msg)


    
    # calculate ToAR  -- ${BAND}_Radiance is already 32-bit -- see above!
 
    #  r.mapcalc "${BAND}_ToAR = \
    #	( ${PI} * ${BAND}_Radiance * ${ESD}^2 ) / ( ${!BAND_Esun} * cos(${SZA}) )"
    #  r.info -r ${BAND}_ToAR

    msg = "Reflectance = ( π * Radiance * ESD^2 ) / BAND_Esun * cos(SZA)"
    g.message(msg)
    toar = "%s = math.pi * %s * %f**2 / %f * %f" \
    % (ref, rad, esd, esun, sza)
    grass.mapcalc(toar)

 
    ## add some metadata
    #r.support map=${BAND}_ToAR \
    #title="echo ${BAND} band (Top of Atmosphere Reflectance)" \
    #units="Unitless planetary reflectance" \
    #description="Top of Atmosphere `echo ${BAND}` band spectral Reflectance (unitless)" \
    #source1='"Radiometric Use of QuickBird Imagery, Technical Note (2005)," by Keith Krause, Digital Globe' \
    #source2="Digital Globe" \
    #history="PI=3.14159265358; K=${!K_BAND}; Bandwidth=${!BAND_Width}; ESD=${ESD}; Esun=${!BAND_Esun}; SZA=${SZA}"
 
###