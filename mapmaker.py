#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 19:51:37 2019

@author: jameseast
"""

import mapgen
import glob

#conc = 'CCTM_D502a_Linux3_x86_64intel.ACONC.BOGOTA_bc2014v3_20140101.nc'
spc = 'PM25'
contour = False
points = True
filename = spc+'gridplot'
title = spc+' OND grid plot'

#i = 1
#c = str(i+1)
#case = 'case'+c

#sectors = ['On-road', 'Industrial', 'Bldg Const', 'Quarrying RPM', \
#         'Main Rd RPM', 'Scndry Rd RPM', 'Unpaved Ind Rd RPM', \
#         'Unpaved Public Rd RPM']

#conc = '/Users/jameseast/Google Drive/Research Projects/' + \
#       'Bogota Project/emissions_scaling/spring2019_PM25/' + \
#       'srccont.'+case+'.nc'
#conc = 'CCTM_D502a_Linux3_x86_64intel.ACONC.BOGOTA_bc2014v3_20140103.nc'      
#conc = '../../../data_out/bc2014v3/d04/2014-10-01/CCTM_D502a_Linux3_x86_64intel.ACONC.BOGOTA_20141001.nc'
conc = glob.glob('../../../data_out/bc2014v3/d04/2014-0[123]-??/CCTM_D502a_Linux3_x86_64intel.ACONC.BOGOTA_20140[123]??.nc')
#sc = sectors[i]
#title = 'Contribution of '+sc+' to '+spc 


mapgen.pointplot( conc, spc, contour, points = points, \
                  filetype = 'pdf', filename=filename, \
                  title=title )
