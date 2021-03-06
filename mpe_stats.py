import numpy as np
import numpy.ma as ma
import xarray as xr
import make_plots as mp
import pm_aggregator as pm
import pandas as pd
import os

def ob_row_col():
    # obcol and obrow are 14 observation site locations
    #obcol = [ 32, 36, 28, 38, 29, 40, 27, 36, 37, 32, 36, 35, 30, 42 ]	
    #obrow = [ 44, 34, 27, 33, 36, 48, 30, 38, 31, 31, 25, 46, 25, 40 ]

    # Without Suba
    obcol = [ 32, 36, 28, 38, 29, 40, 27, 36, 37, 32, 36, 30, 42 ]	
    obrow = [ 44, 34, 27, 33, 36, 48, 30, 38, 31, 31, 25, 25, 40 ]
    return obrow, obcol

def get_spcs():
    obspcs = ['CO','NOx','O3','SO2','PM25','PM10'] # TEMP2 not in monet obj
    modspcs = ['CO','NOx','O3','SO2','PM25','PM10'] # TEMP2 not in monet obj
    return obspcs, modspcs

def get_obs(season=None, avtime=None):
    '''
    season = 'JFM', 'OND', or 'JFMOND'
    avtime = a24, a3, a8, ayr, mda1, mda3, mda8
    keep lat/lon
    Add path to file
    '''
 
    prefix = '/mnt/raid2/Shared/Bogota/observations/ground/' # Bezier
    #prefix = '/ncsu/volume1/fgarcia4/Bogota/observations/ground/' #Henry2
    #prefix = '/rsstu/users/f/fgarcia4/garcia_grp/Bogota/data_eval/observations/ground/' #Henry2
    #prefix = '../obs/' # James Macbook
    prefix = os.path.dirname(os.path.realpath(__file__)) #mac
    prefix = prefix+'/../obs/'#mac
    if season and avtime:
        filename = prefix+'RMCAB_2014_' + season + '-' + avtime + '.nc'
    elif not season and avtime:
        filename = prefix+'RMCAB_2014-' + avtime + '.nc'
    elif season and not avtime:
        filename = prefix+'RMCAB_2014_' + season + '.nc'
    else:
        filename = prefix+'RMCAB_2014.nc'
    print(filename)
    f = xr.open_mfdataset(filename)
    f = f.rename({'PM10STD':'PM10', 'PM25STD':'PM25'})
    try:
        f = f.rename({'TSTEP':'time'})
    except ValueError:
        pass
    f.load()

    # Remove Suba
    l = [f.isel(points=i) for i in range(14)]
    l.pop(11)
    f = xr.concat(l, dim='points')
    separator=';'
    sites = f.SITENAMES.split(separator)
    sites.remove('Suba')
    sites = separator.join(sites)
    f.attrs.update({'SITENAMES':sites})

    return f

def get_met(filelist):
    '''
    filelist = python list of METCRO2D filenames or string of 1 file
    returns xarray dataset of desired met vars
    '''
    flist = []
    if type(filelist) == str:
        flist.append(filelist)
    else:
        flist = filelist
    obrow, obcol = ob_row_col()
    met=[]
    y, x = ob_row_col()
    for i, file in enumerate(flist):
        f = xr.open_dataset(file)
        metvars = [ 'PRSFC', 'TEMP2', 'RN', 'WSPD10', 'WDIR10' ] 
        mid = [j+0.5 for j in range(len(f.TSTEP) - 1)]
        fvars = [ f[v].interp(TSTEP=mid) for v in metvars ]
        met.append(xr.merge(fvars))
        met[i] = met[i].interp(TSTEP = mid)
    met = xr.concat(met, 'TSTEP')
    
    metx = xr.concat( [ met[dict(LAY=[0], ROW=[y], COL=[x])] \
                            for y,x in zip(obrow,obcol)], 'site' )
    metx = metx.squeeze()
    metx = metx.rename({'TSTEP':'time'})
    metx = metx.transpose( 'time', 'site' )
    
    return metx
    # need to set time coords


def get_ad(filelist,cmqversion):
    '''
    filelist = python list of filenames or string of 1 file
    returns a xarray dataset of desired ad vars
    '''
    advars = ['PM25AT','PM25AC','PM25CO']    
    if cmqversion == 'v53':
        advars = advars + ['PM10AT','PM10AC','PM10CO']
    flist = []
    if type(filelist) == str:
        flist.append(filelist)
    else:
        flist = filelist
    f = xr.open_mfdataset(flist, concat_dim='TSTEP')
    fvars = [ f[v] for v in advars ]
    ad = xr.merge(fvars)
    
    obrow, obcol = ob_row_col()
    adx = xr.concat( [ ad[dict(LAY=[0], ROW=[y], COL=[x])] \
                       for y,x in zip(obrow,obcol)], 'site' )
    adx = adx.squeeze()
    adx = adx.rename({'TSTEP':'time'})
    adx = adx.transpose( 'time', 'site' )
    
    return adx

def get_cmaq_gridded(cfilelist, adflist, cmqversion='v502', more_spc=[]):
    '''
    cfilelist = python list of ACONC filenames
    adflist = list of AERODIAM files
    more_spc = list of additional species to aggregate
               Currently limited to PM25_NH4, PM25_NO3, PM25_SO4
               Edit pm_aggregator.py to change to add capability
    cmqversion = version of CMAQ for PM25 species definition.
                 'v502' or 'v53' only
    returns a gridded cmaq object with important vars aggregated
    '''
    if cmqversion == '':
        raise ValueError('Argument cmqversion not specified, must be "v502" or "v53"')
    print('\n \n \nWARNING: CMAQ data is being processed as CMAQ%s'%cmqversion)
    print('If using different version, CHANGE NOW!\n \n \n') 
    d = xr.open_mfdataset(cfilelist, concat_dim='TSTEP')
    d = d.sel(LAY=0) # get only bottom layer

    #obrow, obcol = ob_row_col()
    obspcs, modspcs = get_spcs()
    pmspcs = []
    if ('PM10' in modspcs) or ('PM25' in modspcs):
        if cmqversion == 'v502':
            pmspcs = pm.get_spcs()
        elif cmqversion == 'v53':
            pmspcs = pm.get_spcsv53()
        if 'PM25' in modspcs:
            pm_25 = True
            modspcs.remove('PM25')
        if 'PM10' in modspcs:
            pm_10 = True
            modspcs.remove('PM10')
    allspcs = modspcs + pmspcs + more_spc
    
    if 'NOx' in modspcs:
        d['NOx'] = d.NO2 + d.NO
        units = {'units':d.NO.units}
        d['NOx'].attrs.update(units) #ppmV

    dset = xr.merge([d[var] for var in modspcs]) 

    if pm_25 or pm_10 or more_spc:
        advars = ['PM25AT','PM25AC', 'PM25CO']
        if cmqversion == 'v53':
            advars = advars + ['PM10AT','PM10AC','PM10CO']
        flist = []
        if type(adflist) == str:
            flist.append(adflist)
        else:
            flist = adflist
        f = xr.open_mfdataset(flist, concat_dim='TSTEP')
        f = f.sel(LAY=0)
        fvars = [ f[v] for v in advars ]
        ad = xr.merge(fvars)
        if pm_25 or pm_10:
            if cmqversion == 'v502':
                PM25, PM10 = pm.pm_total2(d, ad)
            elif cmqversion == 'v53':
                PM25, PM10 = pm.pm_totalv53(d, ad)
            PM25 = PM25.to_dataset(name='PM25')
            PM10 = PM10.to_dataset(name='PM10')
            dset = xr.merge([dset, PM25, PM10])
        if 'PM25_NH4' in allspcs:
            PM25_NH4 = pm.pm25_nh4(d, ad)
            PM25_NH4 = PM25_NH4.to_dataset(name='PM25_NH4')
            dset = xr.merge([dset, PM25_NH4])
        if 'PM25_NO3' in allspcs:
            PM25_NO3 = pm.pm25_no3(d, ad)
            PM25_NO3 = PM25_NO3.to_dataset(name='PM25_NO3')
            dset = xr.merge([dset, PM25_NO3])
        if 'PM25_SO4' in allspcs:
            PM25_SO4 = pm.pm25_so4(d, ad)
            PM25_SO4 = PM25_SO4.to_dataset(name='PM25_SO4')
            dset = xr.merge([dset, PM25_SO4])
    
 
    if type(cfilelist) == str:
        t1 = pd.to_datetime(cfilelist[-11:-3]) #YYYMMDD string from file name 
    else:
        t1 = pd.to_datetime(cfilelist[0][-11:-3]) #YYYMMDD string from file name
    dates = pd.date_range(start=t1,periods=len(f.TSTEP.values),freq='H')
    dset = dset.assign_coords(time=dates)
 
    #if type(cfilelist) == str:
        #t1 = pd.to_datetime(cfilelist[-11:-3]) #YYYMMDD string from file name 
    #else:
        #t1 = pd.to_datetime(cfilelist[0][-11:-3]) #YYYMMDD string from file name
    #dates = pd.date_range(start=t1,periods=len(d.TSTEP.values),freq='H')
    #dset = dset.assign_coords(time=dates)
    dset = dset.assign_attrs({'SDATE':d.SDATE})

    # assign units
    for v in dset.variables:
        if v in list(d.variables):
            dset[v] = dset[v].assign_attrs(units=d[v].units)
    
    #fix units
    for v in ['SO2','O3','NOx']:
        if v in modspcs:
            dset[v] = dset[v]*1e3 #ppm to ppb
            dset[v] = dset[v].assign_attrs(units='ppb') 
    for v in ['PM25','PM10']:
        if (v=='PM25' and pm_25) or (v=='PM10' and pm_10):
            dset[v] = dset[v].assign_attrs(units='ug/m3')
    
    # Rename TSTEP dimension
    dset = dset.rename({'TSTEP':'time'})
 
    # Misc attributes
    dset.attrs['SDATE'] = d.SDATE
    dset.attrs['cmqversion']=cmqversion

    del(d)
    
    return dset

def get_cmaq(cfilelist, adflist, cmqversion = 'v502', more_spc=[]):
    '''
    cfilelist = python list of ACONC filenames
    adflist = list of AERODIAM files
    cmqversion = version of CMAQ for PM25 species definition.
                 'v502' or 'v53' only
    returns a monet cmaq object with important vars aggregated
    '''
    if cmqversion == '':
        raise ValueError('Argument cmqversion not specified, must be "v502" or "v53"')
    print('\n \n \nWARNING: CMAQ data is being processed as CMAQ%s'%cmqversion)
    print('If using different version, CHANGE NOW!\n \n \n') 

    f = xr.open_mfdataset(cfilelist, concat_dim='TSTEP')

    mod = []
    obrow, obcol = ob_row_col()
    obspcs, modspcs = get_spcs()
    pmspcs = []
    if ('PM10' in modspcs) or ('PM25' in modspcs):
        if cmqversion == 'v502':
            pmspcs = pm.get_spcs()
        elif cmqversion == 'v53':
            pmspcs = pm.get_spcsv53()
        if 'PM25' in modspcs:
            pm_25 = True
            modspcs.remove('PM25')
        if 'PM10' in modspcs:
            pm_10 = True
            modspcs.remove('PM10')
    allspcs = modspcs + pmspcs
    
    if 'NOx' in modspcs:
        f['NOx'] = f.NO2 + f.NO
        units = {'units':f.NO.units}
        f['NOx'].attrs.update(units) #ppmV
    
    l = []
    for spc in allspcs:
        mod = xr.concat( [f[spc][:,0,y,x] for y,x in zip(obrow,obcol)], 'site' ) 
        l.append(mod)

    modx = xr.merge( l )
    modx = modx.rename({'TSTEP':'time'})
    modx = modx.transpose( 'time', 'site' )
    del(l)
    del(mod)
    #modx = xr.merge([modx[var] for var in modspcs])

    if pm_25 or pm_10 or more_spc:
        adx = get_ad(adflist,cmqversion)
        if pm_25 or pm_10:
            if cmqversion == 'v502':
                PM25, PM10 = pm.pm_total2(modx, adx)
            elif cmqversion == 'v53':
                PM25, PM10 = pm.pm_totalv53(modx, adx)
            PM25 = PM25.to_dataset(name='PM25')
            PM10 = PM10.to_dataset(name='PM10')
            modx = xr.merge([modx, PM25, PM10])
            modspcs.append('PM25')
            modspcs.append('PM10')
        if 'PM25_NH4' in more_spc:
            PM25_NH4 = pm.pm25_nh4(modx, adx)
            PM25_NH4 = PM25_NH4.to_dataset(name='PM25_NH4')
            modx = xr.merge([modx, PM25_NH4])
            modspcs.append('PM25_NH4')
        if 'PM25_NO3' in more_spc:
            PM25_NO3 = pm.pm25_no3(modx, adx)
            PM25_NO3 = PM25_NO3.to_dataset(name='PM25_NO3')
            modx = xr.merge([modx, PM25_NO3])
            modspcs.append('PM25_NO3')
        if 'PM25_SO4' in more_spc:
            PM25_SO4 = pm.pm25_so4(modx, adx)
            PM25_SO4 = PM25_SO4.to_dataset(name='PM25_SO4')
            modx = xr.merge([modx, PM25_SO4])
            modspcs.append('PM25_SO4')
        if 'PM_ANAI' in more_spc:
            PM_ANAI = pm.pm25_anai(modx,adx)
            PM_ANAI = PM_ANAI.to_dataset(name='PM_ANAI')
            modx = xr.merge([modx, PM_ANAI])
            modspcs.append('PM_ANAI')
        if 'PM_AOTHRI' in more_spc:
            PM_AOTHRI = pm.pm25_aothri(modx,adx)
            PM_AOTHRI = PM_AOTHRI.to_dataset(name='PM_AOTHRI')
            modx = xr.merge([modx, PM_AOTHRI])
            modspcs.append('PM_AOTHRI')

    modx = xr.merge([modx[var] for var in modspcs])

    if type(cfilelist) == str:
        t1 = pd.to_datetime(cfilelist[-11:-3]) #YYYMMDD string from file name 
    else:
        t1 = pd.to_datetime(cfilelist[0][-11:-3]) #YYYMMDD string from file name
    dates = pd.date_range(start=t1,periods=len(f.TSTEP.values),freq='H')
    modx = modx.assign_coords(time=dates)
    
    #fix units
    for var in ['SO2','O3','NOx']:
        if var in modspcs:
            modx[var] = modx[var]*1e3 #ppm to ppb
            modx[var] = modx[var].assign_attrs(units='ppb') 
    
    
    # This part to add Bogota city average dataarray
    # to the xarray dataset object
    #prefix = '/mnt/raid2/Shared/Bogota/data_eval/scripts/bogota_cmaq_mpe/'
    prefix = os.path.dirname(os.path.realpath(__file__)) # cwd for this script
    bog_array = xr.open_dataset(prefix+'/bogota_area_cells.nc')
    bog_array = bog_array.bogota_city_cell
    bog_array.load()

    f = f.sel(LAY=0)

    adf = xr.open_mfdataset(adflist, concat_dim='TSTEP')
    adf = adf.sel(LAY=0) 
    advars = ['PM25AT','PM25AC', 'PM25CO']
    fvars = [ adf[v] for v in advars ]
    ad = xr.merge(fvars)

    if pm_25:
        if cmqversion == 'v502':
            PM25, PM10 = pm.pm_total2(f, adf)
        elif cmqversion == 'v53':
            PM25, PM10 = pm.pm_totalv53(f, adf)

    a1 = PM25*bog_array.rename({'lat':'ROW','lon':'COL'})
    a2 = a1.sum(dim=('ROW','COL'))
    bog_avg = a2/bog_array.sum()
    bog_avg = bog_avg.to_dataset(name='bog_avg_PM25')
    bog_avg = bog_avg.rename({'TSTEP':'time'})

    modx = xr.merge([modx,bog_avg])    
    modx.attrs['cmqversion']=cmqversion
    modx.attrs['SDATE']=f.SDATE
    del(f)
    return modx



def pair_data(obs, modx, metx, metfullszn=True):
    '''
    statistic = NME, NMB, r2
    dates optional if not entire dataset
    sites optional, obs sites
    std or local conditions pm??
    prints stat results
    returns model and obs paired value arrays
    'ad' file is requried for PM speciation, only used for pm speciation
    '''
    
    obspcs, modspcs = get_spcs()
        
    obrow, obcol = ob_row_col()
#    nsites = len(obcol)

    shour, nhours = get_start_date(modx)
    print('start = %d, number of hours = %d' % (shour, nhours))

    # get all obs vals and create xarray dataset for them
    obx = xr.merge([obs[spc].isel(time=slice(shour,shour+nhours)) for spc in obspcs])
    print(obx)
    obx = obx.assign_coords(time=modx.time)
    obx = obx.rename({'points':'site'})
    obx = obx.transpose( 'time', 'site' )
 
    metx.load()
    modx.load()
    obx.load()
    obx.attrs = obs.attrs
    if metfullszn == True:
        if modx.cmqversion == 'v53': # Do this for v53 when METCRO2D file has entire season
            metx = metx.sel(time=slice(shour,shour+nhours))
    metx = metx.assign_coords(time=modx.time)
    # Set PM10 and PM25 to std
    std = ['PM10','PM25']
    for i in std:
        if i in modspcs:
            modx[i] = modx[i]*metx.TEMP2/298.15*101325./metx.PRSFC

    return obx, modx, metx


def calc_mda8(d):
    '''
    Calculate mda8 for O3
    observation and model dataset
    borrowed from http://danielrothenberg.com/
    gcpy/examples/timeseries/calc_mda8_timeseries_xarray.html
    '''
    
    # time adjustment so mda8 value references 1st hour in 
    # the rolling average
    times_np = d.O3.time.values.copy()
    times_pd = pd.to_datetime(times_np) - pd.Timedelta('7h')

    o3a8 = d.O3.rolling(time=8, min_periods=6).mean()
    o3a8 = o3a8.assign_coords(time=times_pd)
    o3_mda8 = o3a8.resample(time='D').max(dim='time')
    length = len(o3_mda8.time)
    o3_mda8 = o3_mda8.isel(time=slice(1,length)) # Remove extra 1st max val b/c time shift

    o3_mda8 = o3_mda8.assign_attrs({'units':'ppb'})
    
    # Try to assign sitenames. Will only work if observation dataset used.
    try:
        o3_mda8 = o3_mda8.assign_attrs({'SITENAMES':d.SITENAMES})
    except:
        pass

    return o3_mda8


def calc_stats(obx, modx):

    sites = obx.SITENAMES.split(';')

    obspcs, modspcs = get_spcs()

    nmedata = np.ma.zeros((len(sites), len(obspcs), 2))
    nmbdata = np.ma.zeros((len(sites), len(obspcs), 2))
    r2data  = np.ma.zeros((len(sites), len(obspcs), 2))
    mfedata = np.ma.zeros((len(sites), len(obspcs), 2))
    mfbdata = np.ma.zeros((len(sites), len(obspcs), 2))
    
    obx24, modx24 = make_24h_avg(obx, modx)    

    #calc mda8 for ozone only
#    print(modx.time)
    o3_mda8_ob = calc_mda8(obx)
    o3_mda8_mod = calc_mda8(modx)
#    print(modx.time)
    
    mda8obm = ma.masked_invalid(o3_mda8_ob.values) 
    mda8modm = ma.array(o3_mda8_mod.values, mask=mda8obm.mask)

    # do stat calcs at sites
    for i in range(len(sites)):
        for obspc,modspc in zip(obspcs,modspcs):
           
            ovalmasked = ma.masked_invalid( \
                         obx[obspc][:,i].values ) # mask obs array
            ovalmasked24 = ma.masked_invalid( \
                           obx24[obspc][:,i].values ) # mask obs array 24hr avg
            mvalmasked = ma.array( modx[modspc][:,i].values, \
                                   mask=ovalmasked.mask ) # apply obs mask to mod array
            mvalmasked24 = ma.array( modx24[modspc][:,i].values, \
                                     mask=ovalmasked24.mask ) # for 24hr avg
          
            # apply 40 ppb cutoff for hourly O3
            if obspc == 'O3':
                ovalmasked = ma.masked_where(ovalmasked<=40,ovalmasked)
                mvalmasked = ma.array(mvalmasked, mask=ovalmasked.mask)
            
            r2data[i,obspcs.index(obspc),0] = calc_r2(mvalmasked, ovalmasked)
            nmedata[i,obspcs.index(obspc),0] = calc_NME(mvalmasked, ovalmasked)
            nmbdata[i,obspcs.index(obspc),0] = calc_NMB(mvalmasked, ovalmasked)
            mfedata[i,obspcs.index(obspc),0] = calc_MFE(mvalmasked, ovalmasked)
            mfbdata[i,obspcs.index(obspc),0] = calc_MFB(mvalmasked, ovalmasked)
            
            if obspc == 'O3':
                # mda8 stats, ozone only
                r2data[i,obspcs.index(obspc),1] = calc_r2(mda8modm[:,i], mda8obm[:,i])
                nmedata[i,obspcs.index(obspc),1] = calc_NME(mda8modm[:,i], mda8obm[:,i])
                nmbdata[i,obspcs.index(obspc),1] = calc_NMB(mda8modm[:,i], mda8obm[:,i])
                mfedata[i,obspcs.index(obspc),1] = calc_MFE(mda8modm[:,i], mda8obm[:,i])
                mfbdata[i,obspcs.index(obspc),1] = calc_MFB(mda8modm[:,i], mda8obm[:,i])
            else:
                # 24hr for all other species
                r2data[i,obspcs.index(obspc),1] = calc_r2(mvalmasked24, ovalmasked24)
                nmedata[i,obspcs.index(obspc),1] = calc_NME(mvalmasked24, ovalmasked24)
                nmbdata[i,obspcs.index(obspc),1] = calc_NMB(mvalmasked24, ovalmasked24)
                mfedata[i,obspcs.index(obspc),1] = calc_MFE(mvalmasked24, ovalmasked24)
                mfbdata[i,obspcs.index(obspc),1] = calc_MFB(mvalmasked24, ovalmasked24)

    stats = xr.Dataset({'NME': (['site','species','averagingtime'], nmedata),   \
                        'NMB': (['site','species','averagingtime'], nmbdata),   \
                        'R2': (['site','species','averagingtime'], r2data),     \
                        'MFE': (['site','species','averagingtime'], mfedata),   \
                        'MFB': (['site','species','averagingtime'], mfbdata)},  \
                       coords = {'site': sites, 'species': obspcs, \
                                 'averagingtime': ['hourly','24h/mda8']})

    return stats

def stats_all_sites( obx, modx ):
    '''
    takes as input obs and mod xarrays
    returns a dictionary: {'species': (tuple of stat metrics)}
    Order of return tuple: ( meanob, nme, nmb, r2, mfe, mfb, maxob )
    '''
    avstats = dict()
    #for var, i in zip(obx.data_vars, range(len(obx.data_vars))):
    #for i, var in enumerate(obx.data_vars)
    for var in obx.data_vars:
        arro = np.concatenate(obx[var].values)
        arrm = np.concatenate(modx[var].values)
        mask = np.isnan(arro)
        arro, arrm = ma.array(arro, mask=mask), ma.array(arrm, mask=mask)
        #if not arro.count() == 0: 
        nme = calc_NME( arrm, arro )
        nmb = calc_NMB( arrm, arro )
        mfe = calc_MFE( arrm, arro )
        mfb = calc_MFB( arrm, arro )
        r2 = calc_r2( arrm,arro )
        meanob  = np.mean( arro )
        maxob = np.max(arro)
        avstats[var] = ( meanob, nme, nmb, r2, mfe, mfb, maxob )
    return avstats

def plot_scatter( obx, modx ):
    if not list(obx.keys()) == list(modx.keys()):
        raise ValueError('Modeled and observed dataset variables do not match')
    obx24, modx24 = make_24h_avg(obx,modx)
    for var in list(obx.keys()):
        # hourly
        fname = '%s_scatter' % (obx[var].name)
        mp.make_scatter(obx, modx, var, fname)
        # 24 hour avg
        if var == 'O3':
            o3_mda8_ob = calc_mda8(obx)
            o3_mda8_mod = calc_mda8(modx)
            fname24 = 'O3_scatter_mda8'
            mp.make_scatter(o3_mda8_ob, o3_mda8_mod, var, fname24)
        else:
            fname24 = '%s_scatter_24hr' % (obx24[var].name)
#            if var == 'PM10':
#                print(obx24)
#                print(modx24)
            mp.make_scatter(obx24, modx24, var, fname24)

def plot_stats( obx, modx, season):
    if not list(obx.keys()) == list(modx.keys()):
        raise ValueError('Modeled and observed dataset variables do not match')
    stats = calc_stats( obx, modx )
    obx24, modx24 = make_24h_avg(obx, modx)
    avstats = stats_all_sites( obx, modx )
    avstats24 = stats_all_sites( obx24, modx24)
    o3mda8 = calc_mda8(obx)
    for var in stats.species.values:
#        for metric in ['NME', 'NMB', 'R2']:
        for metric in ['NME', 'NMB','MFB','MFE','R2']:
            # hourly
            avtime = 'hourly'
            if not np.isnan( stats[metric].loc[:,var,avtime] ).all():
                mp.make_stat_plots(stats, avstats, obx, metric, var,season, avtime)
            # 24 hour avg
            avtime = '24h/mda8'
            if var=='O3':
                #stuff
                if not np.isnan( stats[metric].loc[:,var,avtime] ).all():
                    mp.make_stat_plots(stats, avstats24, obx, metric, var,season, 'mda8', o3mda8)               
            else:
                if not np.isnan( stats[metric].loc[:,var,avtime] ).all():
                    mp.make_stat_plots(stats, avstats24, obx24, metric, var,season, '24h')
            
def make_24h_avg(obx, modx):
    obx24 = obx.resample(time='D', keep_attrs=True).mean()
    obx24.attrs = obx.attrs
    for var in list(obx.keys()):
        if not var == 'time_bounds':
            obx24[var].attrs = obx[var].attrs
    modx24 = modx.resample(time='D', keep_attrs=True).mean()
    return obx24, modx24

def get_start_date(cmaq):
    '''
    Input: xarray dataset (cmaq output, must have SDATE attribute)
    Returns start hour (shour), where hour 0 is 12:00am, Jan 1, 2014
    to match first observed hour
    Returns length of model output in hours (nhours)
    '''
    sdate = cmaq.SDATE
    if sdate > 2014273: #OND
        shour = sdate - 2014273 - 1
    else: #JFM
        shour = sdate - 2014000 - 1
    shour = shour * 24
    nhours = len(cmaq.time)
    return shour, nhours

def calc_r2(model, obs):
    '''
    need to calc confidence interval
    input is masked numpy.ndarray from xrdataset.variables.values
    input is matching array
    '''
    r = np.ma.corrcoef(model, obs)[0,1]
    return r**2

def calc_NME(modeled, obs):
    '''
    return a value
    '''	
    return ( np.sum( np.abs(modeled - obs) ) / np.sum(obs) ) * 100

def calc_NMB(modeled, obs):
    '''
    return a value
    '''
    return ( np.sum( modeled - obs ) / np.sum(obs) ) * 100

def calc_MFB(mod, obs):
    '''
    return a value
    '''
    return (1/obs.count()) * np.sum( (mod-obs)/((mod+obs)/2) ) * 100

def calc_MFE(mod, obs):
    '''
    return a value
    '''
    return (1/obs.count()) * np.sum( np.abs(mod-obs)/((mod+obs)/2) ) * 100

