from __future__ import print_function
import xarray as xr
import Ngl as ngl
import Nio as nio
import numpy as np
from monet.models import cmaq
import mpe_stats as mpe
import math

def spacing(nintvls, maxc, clen):
    lspc = round( maxc / (nintvls), 2 )
    maxl = round(maxc,2)
    minl = lspc
    print('maxlvl = %s, spacing = %s, min = %s, num = %s' % (maxl,lspc,minl,nintvls))
    return maxl,lspc,minl


def pointplot( conc, spc, season, contour = False, points = True, filetype = 'pdf',\
          filename = 'pointplot', title=False ):
    '''
    conc: string of file path(s). cctm output file(s). Averages across all files
          for plot.
    spc: string. species to be plotted
         TEMP2, CO, PM10, PM25, NO2, PRSFC, NOx, NO, O3, RAIN, SO2
    contour: Boolean. contour plot if True, grid if False (default is False)
    points: Boolean. add observation data points to plot (default is True)
    filetype: string, (default is 'pdf') 
    filename: String
    title: optional string of title on map
    
    Function uses PyNGL library to plot cmaq data with obs data on top as points.
    CCTM file path(s) are supplied to function by user
    RMCAB observation filepaths are hardcoded
    '''
    
    conc = conc
    filetype = filetype
    filename = filename
    spc = spc
    season = season   
 
    # Get AERODIAM file for PM aggregation
    adflist = conc
    if type(adflist) == str:
        adflist = adflist.replace('ACONC','AERODIAM')
    else:
        adflist = [adflist[n].replace('ACONC','AERODIAM') for n in range(len(adflist))]
    
    # Grid file used for lat/lon only. Date does not matter.
    grid = '../../../data_in/mcip/v4n/d04/GRIDCRO2D_WRFd04v4n_2014-01-01'
    
    font = "helvetica" # {21,    "helvetica"}
    fontheight = 0.02
    
    # Open obs using xarray, open conc with Monet for aggregate PM spcs
    #f = nio.open_file(conc,"r")
    f = mpe.get_cmaq_gridded(conc, adflist)
    fgrid = xr.open_dataset(grid)
    print(f[spc])
    units = f[spc].units
    if spc in ('PM25', 'PM10'):
        units = 'ug/m3'
    
    # Open observed dataset
    fob = mpe.get_obs(season=season, avtime='a24')
    # Get days matching model input
    shour, nhours = mpe.get_start_date(f)
    print(shour, nhours)
    # subset observtion dataset
    ind1 = math.floor(shour/24)
    ind2 = math.floor(nhours/24)
    obdata = fob[spc][:, ind1:ind2].squeeze()
    obdata = obdata.mean(dim='time')
    
    # get obs sites lats and lons
    oblat = fob['latitude'].values
    oblon = fob['longitude'].values

    # a numpy array of lat and lon
    lat = fgrid.variables["LAT"].values[0,0,:,:]
    lon = fgrid.variables["LON"].values[0,0,:,:]
    
    # make a numpy arraya to plot
    varobj = f.variables[spc].mean(dim='time')
    var = varobj.values
    print('shape = %s' % str(np.shape(var)))
    if spc == 'CO':
        var = var*1e-3
        units = obdata.units
    elif spc == 'NOx':
        var = var*1e3
        units = obdata.units
        
    # plot filled contour map
    res = ngl.Resources()
    res.nglFrame = False
    
    # start the graphics
    wks = ngl.open_wks(filetype,filename)
    
    # resource settings
    minlat = np.min(lat)
    maxlat = np.max(lat)
    minlon = np.min(lon)
    maxlon = np.max(lon)
    
    
    # color map for contour lines
    res.cnFillOn = True
#    res.cnFillPalette = "MPL_viridis"
    #res.cnFillPalette = "MPL_cool"
    #res.cnFillPalette = "cmocean_matter"
    #res.cnFillPalette = "cmocean_dense"
    #res.cnFillPalette = 'precip3_16lev'
#    res.cnFillPalette = 'BlAqGrYeOrReVi200'
#    res.cnFillPalette = 'MPL_jet'
#    res.cnFillPalette = 'perc2_9lev'
#    res.cnFillPalette = 'cmocean_deep'
    #res.cnFillPalette = 'NCV_bright'
    res.cnFillPalette = 'MPL_rainbow'
    
    # save colormap as array for use with points
    cmap = ngl.read_colormap_file(res.cnFillPalette)
    #cmap = ngl.read_colormap_file('MPL_viridis')
    #cmap = cmap[1::,:] #cut off white
    #res.cnFillColors = cmap
    
    
    res.cnLinesOn = False
    res.cnLineLabelsOn = False
    
    
    # map viewport
    res.mpLimitMode = "LatLon"
    res.mpMinLatF  = minlat
    res.mpMaxLatF  = maxlat
    res.mpMinLonF  = minlon
    res.mpMaxLonF  = maxlon
    res.mpGridAndLimbOn = False
    res.mpFillOn = False #changed 
    
    # tick marks
    res.tmXBLabelFontHeightF = fontheight
    res.tmYLLabelFontHeightF = fontheight
    
    # title text
    if title:
        res.tiMainString = title
    else:
        res.tiMainString = ( '%s Pointplot' % spc)
    res.tiMainFont = font
    res.tiMainFontHeightF   = fontheight
    
    res.sfXArray = lon
    res.sfYArray = lat
    
    # label bar resources
    res.lbPerimThicknessF = 5.0
    res.lbBoxEndCapStyle = 'RectangleEnds' #'TriangleBothEnds'
    #res.lbBoxLineThicknessF = 5.0
    res.lbBoxLinesOn = True #False
    res.lbBoxSeparatorLinesOn = False
    res.lbLabelFont = font
    res.lbLabelFontHeightF = fontheight
    res.lbLabelStride = 5
    
    
    # Set contour line level resources manully 
    res.cnLevelSelectionMode = "ManualLevels"	# manually set the contour 
                                                #levels with the following 3 resources
    if points:
        print('maxc = max( np.max( var ), np.max(obdata).values )')
        print('np.max( var ) = ')
        print(np.max(var))
        print('np.max(obdata).values = ')
        print(np.max(obdata).values)
        maxc = max( np.max( var ), np.max(obdata).values ).item(0)
        print('maxc = ')
        print(type(maxc))
    else:
#        maxc = np.max( var )
        maxc = 13.
    clen = np.shape(cmap)[0]
    nintvls = 15
    if clen < nintvls:
        nintvls = clen - 1
    maxlvl, space, minlvl = spacing( nintvls, maxc, clen )
    res.cnLevelSpacingF = space # set the interval between contours
    res.cnMaxLevelValF  = maxlvl	# set the maximum contour level
    res.cnMinLevelValF  = minlvl	 # set the minimum contour level
    #res.cnLevelSpacingF = round( maxc / (clen-2), 2 ) # set the interval between contours
    #res.cnMaxLevelValF  = round(maxc,1)# + res.cnLevelSpacingF	# set the maximum contour level
    #res.cnMinLevelValF  = res.cnLevelSpacingF	 # set the minimum contour level
    
    print(res.cnLevelSpacingF)
    print(res.cnMaxLevelValF)
       
    # Maximize and size fram
    #res.gsnMaximize = True
    #res.wkPaperHeightF = 8    
    #res.wkPaperWidthF = 8    
 
    if contour:  
        # make plot
        plot = ngl.contour_map(wks,var,res)
        ngl.draw(plot)
    else:
        res.cnFillMode = "CellFill"  # Turn on raster fill
        npts = 64
        res.sfXArray = np.linspace(np.min(lon), np.max(lon),npts+1)
        res.sfYArray = np.linspace(np.min(lat), np.max(lat),npts+1)
        plot = ngl.contour_map(wks,var,res)
      
    
    # open shapefile
    gisf = './gis/LocalidadesBogota.shp'
    shpf = nio.open_file(gisf,"r")
    gislon = np.ravel(shpf.variables['x'][:])
    gislat = np.ravel(shpf.variables['y'][:])
    segments = shpf.variables["segments"][:,0]
    
    # polyline resource settings
    plres = ngl.Resources()
    plres.gsLineColor = "black"
    plres.gsLineThicknessF = 2
    plres.gsSegments = segments
    
    lnid = ngl.add_polyline(wks, plot, gislon, gislat, plres)
    
    # Now draw points on plot
    print('making the plot')
    for i,n in enumerate(obdata):
        if not np.isnan( n.values ):
            print('n not nan, got: %f' % n.values)
            pmres = ngl.Resources()
            indices = np.linspace(start = 0, stop = clen-1, num = nintvls, dtype = int)
            ind = int( np.floor( n.values / res.cnLevelSpacingF) )
            try:
                ind = indices[ind]
            except IndexError:
                ind = indices[ind-1]
            print('ind = %d' % ind)
            print( '' )
            try:
                pmres.gsMarkerColor = cmap[ind,:] # if ob out of color index
            except IndexError:
                pmres.gsMarkerColor = cmap[-1,:] # set ob to greatest color index
            # Add colored markers
            pmres.gsMarkerIndex = 1
            pmres.gsMarkerSizeF = 0.1 # size of marker
            markerfill = ngl.add_polymarker(wks, plot, oblon[i], oblat[i], pmres)
            # Add marker outlines
            pmres.gsMarkerIndex = 4
            pmres.gsMarkerSizeF = pmres.gsMarkerSizeF * 0.24 # size of marker
            pmres.gsLineThicknessF = 10 # marker line thickness
            pmres.gsMarkerColor = 'white'
            markeroutline = ngl.add_polymarker(wks, plot, oblon[i], oblat[i], pmres)
            #add another outline to make it thicker
            pmres.gsMarkerSizeF = pmres.gsMarkerSizeF * 0.93 
            markeroutline = ngl.add_polymarker(wks, plot, oblon[i], oblat[i], pmres)
            pmres.gsMarkerSizeF = pmres.gsMarkerSizeF * 0.93 
            markeroutline = ngl.add_polymarker(wks, plot, oblon[i], oblat[i], pmres)
    
    # text on plot
    txres = ngl.Resources()
    txres.txFont = font
    txres.txFontHeightF = fontheight
#    txres.txFontColor = 'white'
    
    #ngl.text_ndc(wks,varobj.attributes['long_name'], 0.14,0.86,txres)
    #ngl.text_ndc(wks,varobj.attributes['units'], 0.88,0.84,txres)
#    ngl.text_ndc(wks,spc, 0.14,0.86,txres)
    ngl.text_ndc(wks,units, 0.87,0.85,txres)
    
    
    #-- advance the frame
    ngl.draw(plot)
    
    
    maxtxt = 'MAX: %5.1f %s' % (np.max(var), units)
    ngl.text_ndc(wks, maxtxt, 0.28, 0.77,txres)
    
    ngl.frame(wks)
    
    ngl.end()
    

