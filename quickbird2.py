# -*- coding: utf-8 -*-
"""
@author: nik | Created on Tue Nov 11 23:53:18 2014
"""

"""
Source: Radiometric Use of QuickBird Imagery, Technical Note.
        2005-11-07, by Keith Krause.
"""

"""
QuickBird2 Band-Averaged Solar Spectral Irradiance [W/sq.m./μm]

Retrieving Esun for a band:
    Esun[band]
"""
Esun = {'Pan': 1381.79,
        'Blue': 1924.59, 'Green': 1843.08, 'Red': 1574.77,
        'NIR': 1113.71}

"""
Factors for Conversion to Top-of-Atmosphere Spectral Radiance
    (absolute radiometric calibration factors)

Structure of the dictionary:
- Key: Name of band
- Items in tupple(s):
- 1st: Effective Bandwidth [μm] (relative spectral radiance response)
- Conversion Factors for MSx & Pan (incl. TDI Levels)
    - 2nd: k' revised conversion factors for 8-Bit  products [W/sq.m./sr/count]
    - 3rd: K revised conversion factors for 16-Bit  products [W/sq.m./sr/count]
    
Retrieving values:    
    band = <Name of Band>
    K[band][0]  # for  Effective BandWidth
    K[band][1]  # for k' (8-bit)
    K[band][2]  # for K (16-bit)
"""
KCF = {
    'Pan10': (0.398, 1.02681367, 0.08381880),
    'Pan13': (0.398, 1.02848939, 0.06447600),
    'Pan18': (0.398, 1.02794702, 0.04656600),
    'Pan24': (0.398, 1.02989685, 0.03494440),
    'Pan32': (0.398, 1.02739898, 0.02618840),
    'Blue':  (0.068, 1.12097834, 0.01604120),
    'Green': (0.099, 1.37652632, 0.01438470),
    'Red':   (0.071, 1.30924587, 0.01267350),
    'NIR':   (0.114, 1.98368622, 0.01542420)}
