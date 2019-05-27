#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 19:51:37 2019

@author: jameseast
"""

import maptest2

#conc = 'CCTM_D502a_Linux3_x86_64intel.ACONC.BOGOTA_bc2014v3_20140101.nc'
spc = 'O3'
contour = False
points = True
filename = 'O3gridplot'
title = 'O3 grid plot'

#i = 1
#c = str(i+1)
#case = 'case'+c

#sectors = ['On-road', 'Industrial', 'Bldg Const', 'Quarrying RPM', \
#         'Main Rd RPM', 'Scndry Rd RPM', 'Unpaved Ind Rd RPM', \
#         'Unpaved Public Rd RPM']

#conc = '/Users/jameseast/Google Drive/Research Projects/' + \
#       'Bogota Project/emissions_scaling/spring2019_PM25/' + \
#       'srccont.'+case+'.nc'
conc = 'CCTM_D502a_Linux3_x86_64intel.ACONC.BOGOTA_bc2014v3_20140103.nc'      

#sc = sectors[i]
#title = 'Contribution of '+sc+' to '+spc 


maptest2.pointplot( conc, spc, contour, points = points, \
                   filetype = 'pdf', filename=filename, \
                   title=title )