#created with matplotlib 3.0.2
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def colorlist():
    # 19 distinct colors from
    # https://sashat.me/2017/01/11/list-of-20-simple-distinct-colors/
#    colors = [(230, 25, 75), (60, 180, 75), (255, 225, 25), (0, 130, 200),\
#              (245, 130, 48), (145, 30, 180), (70, 240, 240), (240, 50, 230),\
#              (210, 245, 60), (250, 190, 190), (0, 128, 128), (230, 190, 255),\
#              (170, 110, 40), (255, 250, 200), (128, 0, 0), (170, 255, 195),\
#              (128, 128, 0), (255, 215, 180), (0, 0, 128)]
    colors = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231',\
              '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabebe',\
              '#469990', '#e6beff', '#9A6324', '#fffac8', '#800000',\
              '#aaffc3', '#808000', '#ffd8b1', '#000075',]
#    colors = [str(t) for t in colors] # convert tuples to strings
    return colors
    

def make_scatter( obx, modx, var, fname):
    '''
    x and y are xarray datasets 
    with matching dims
    x = observed
    y = modeled
    var = string of spcs of interest
    e.g. modx.CO is input
    '''
    
    sites = obx.SITENAMES.split(';')
    nsites = len(obx.site)
    if var == 'O3' and fname[-4:] == 'mda8':
        obx = obx
        modx = modx
    else:
        obx = obx[var]
        modx = modx[var]
    
    if var in ('PM25', 'PM10'):
        units = '$\mu g/m^3$'
    else:
        units = obx.units
    


    plt.style.use(['seaborn-white', 'seaborn-ticks'])
    frmt = 'pdf'
    #fname = obx.name+'scatter'
    #color = 'red' 
    fig, ax = plt.subplots(1)

    maxx = np.max(obx)
    maxy = np.max(modx)
    axlim = max(maxx, maxy)*1.1 
    axlim = axlim.values

    colors = colorlist()

    # Make diagonal line
    xy = np.linspace(0,axlim,2)
    ax.plot(xy,xy,color='black',lw=1)

    for i in range(nsites):
        if not np.isnan(obx[:,i].values).all():
            ax.scatter(obx[:,i], modx[:,i], marker='o', alpha = 0.7, \
                       c=colors[i], edgecolor='black', s=50, lw = 0.5, \
                       label=sites[i] )

    
    #ax.set_title('%s (%s)' % (obx.name, obx.units))
    #ax.set_xlabel('observed')
    #ax.set_ylabel('modeled')
    #ax.set_xlim([0,axlim])
    #ax.set_ylim([0,axlim])
    
    ax.axis('equal')
    ax.set(xlabel='observed', ylabel='modeled', title='%s (%s)' % \
           (var, units), xlim=[0,axlim], ylim=[0,axlim])

    ax.legend(loc='upper left', fontsize=10, bbox_to_anchor=(1.01,1.01), \
              frameon=False)
    ax.set_aspect('equal','box')
    #plt.style.context('ggplot')

    fig.savefig('../figs/%s.%s' % (fname,frmt), format=frmt, bbox_inches='tight')
    plt.close()

def make_stat_plots(stats,avstats,obx,metric,var,avtime='hourly',o3mda8=None):
    '''
    stats = stats xarray
    avstats: Must be for proper averaging time!
    obx: Must be for proper averaging time!
    modx
    var
    avtime = 'hourly' or '24h' or 'mda8'
    '''
    avtime = avtime.lower()
    metric = metric.upper()
    if avtime not in ('hourly', '24h', 'mda8'):
        raise ValueError("avtime must be 'hourly', '24h', or 'mda8', %s was given" % \
                         (avtime))

    sites = obx.SITENAMES.split(';')
    units = obx[var].units

    plt.style.use(['seaborn-white', 'seaborn-ticks'])
    
    frmt = 'pdf'
    fname = '%s_%s_%s' % (var, metric, avtime)
    
    fig, ax = plt.subplots(1)
    
    colors = colorlist()
    fs=10 #fontsize

    for i, site in enumerate(stats.site):
        # get mean obs if it's not empty
        if not np.isnan(obx[var][:,i]).all():
#            x = np.mean(obx[var][:,i])
            if var == 'O3' and metric == 'mda8':
                if o3mda8 == None:
                    raise ValueError('Argument o3mda8 must be specified for'+\
                                      'ozone MDA8 plotting. No argument was given.')
                x = np.nanmax(o3mda8[:,i])
            else:
                x = np.nanmax(obx[var][:,i])
            # get nme value
            if avtime in ('24h', 'mda8'):
                avtime = '24h/mda8'
            y = stats[metric].loc[site.values,var,avtime]
            if not np.isnan(y):
                ax.scatter( x, y, marker='o', c=colors[i], edgecolor='black',\
                            s=150, lw = 1, label=site.values)
                
    criteria = 0
    goal = 0
    ymin, ymax = ax.get_ylim()

    # Set max x val for plotting mean of all sites
    if var == 'O3':
        x = np.nanmax(o3mda8)
    else:
        x = avstats[var][6]

    # Set criteria & goal lines, y lims if applicable, y val for mean of all sites
    del(goal)
    del(criteria)
    if metric == 'NME':
        y = avstats[var][1]
        ymin = 0
        ymax = 200
        if var == 'O3':
            criteria = 25
            goal = 15
        if var == 'PM25':
            criteria = 50
            goal = 35
    elif metric == 'NMB':
        y = avstats[var][2]
        ymin = -100
        ymax = 200
        if var == 'O3':
            criteria = 15
            goal = 5
        if var == 'PM25':
            criteria = 30
            goal = 10
    elif metric == 'MFE':
        y = avstats[var][4]
        print('MFE y = %f' % y)
        ymin = 0
        ymax = 200
        if var in ('PM10', 'PM25'):
            criteria = 75
            goal = 50
    elif metric == 'MFB':
        y = avstats[var][5]
        print('MFB y = %f' % y)
        ymin = -200
        ymax = 200
        if var in ('PM10','PM25'):
            criteria = 60
            goal = 30
    elif metric == 'R2':
        y = avstats[var][3]
        ymin = 0
        ymax = 1
        if var == 'O3':
            criteria = 0.50**2
            goal = 0.75**2
        if var == 'PM25':
            criteria = 0.40**2
            goal = 0.70**2
    else:
        raise ValueError("Invalid metric, expected 'NME','NMB', 'MFE','MFB'\
                         or 'R2'. Received %s" % (metric))
    print('ALL MARKER = %f, %f' % (x,y))
    ax.scatter( x, y, marker='D', c='black', s=50, label='All')
    ax.annotate('All', (x, y), fontsize=fs)
    xmin, xmax = ax.get_xlim()
    lw = 1

    if var in ('PM25', 'O3'):
        ax.plot([xmin, xmax],[criteria, criteria],'k-', linewidth=lw, \
                label='criteria')
        ax.plot([xmin, xmax],[goal, goal],'k--', linewidth=lw, label='goal')
        if metric == 'NMB' or 'MFB':
            ax.plot([xmin, xmax],[-criteria, -criteria],'k-', linewidth=lw)
            ax.plot([xmin, xmax],[-goal, -goal],'k--', linewidth=lw)
    else:
        ax.plot([xmin, xmax],[0,0],'k-', linewidth=lw)

    ax.set(xlabel='max obs (%s)'%(units), ylabel='%s (%%)'%(metric), \
           title=obx[var].name, ylim=[ymin,ymax], xlim=[xmin,xmax] )

    ax.legend(loc='center left', bbox_to_anchor=(1.01,0.5),\
              frameon=False, fontsize=fs)

    ax.title.set_fontsize(fs)
    ax.xaxis.label.set_fontsize(fs)
    ax.yaxis.label.set_fontsize(fs)
    ax.tick_params(labelsize=fs)
    fig.savefig('../figs/%s.%s' % (fname,frmt), format=frmt, bbox_inches='tight')
    plt.close()
    del(goal)
    del(criteria)


if __name__ == '__main__':
    import glob
    import mpe_stats as mpe
    fo = mpe.get_obs(season='JFM')
    cfiles = glob.glob('CCTM_D502a_Linux3_x86_64intel.ACONC.'+\
                       'BOGOTA_bc2014v3_2014010[123].nc')
    mfiles = glob.glob('METCRO2D_WRFd04v4n_2014-01-0[123]')
    cfiles.sort()
    mfiles.sort()
    fc = mpe.get_cmaq(cfiles)
    fm = mpe.get_met(mfiles)
    obx,modx,metx = mpe.pair_data(fo,fc,fm)
    #print(obx)
    stats = mpe.calc_stats(obx, modx)
    avstats = mpe.stats_all_sites(obx, modx)
    obx24, modx24 = mpe.make_24h_avg(obx,modx)
    avstats24 = mpe.stats_all_sites(obx24, modx24)
    make_scatter(obx,modx,'PM25', 'pm25scatter')
    make_scatter(obx24, modx24, 'PM25', 'pm25scatter24hr')
    m, o3mda8, o3mda8ake_stat_plots(stats,avstats24,obx24,'MFE','PM25',avtime='24h')
    make_stat_plots(stats,avstats24,obx24,'MFB','PM25',avtime='24h')
    make_stat_plots(stats,avstats,obx,'MFE','PM25',avtime='hourly')
    make_stat_plots(stats,avstats,obx,'MFB','PM25',avtime='hourly')
#    make_stat_plots(stats,avstats,obx,'NME','PM25',avtime='hourly')
#    make_stat_plots(stats,avstats,obx,'NME','O3',avtime='hourly')
#    make_stat_plots(stats,avstats,obx,'NMB','PM25',avtime='hourly')
#    make_stat_plots(stats,avstats,obx,'NMB','O3',avtime='hourly')
#    make_stat_plots(stats,avstats,obx,'r2','PM25',avtime='hourly')
#    make_stat_plots(stats,avstats,obx,'r2','O3',avtime='hourly')
#    make_stat_plots(stats,avstats,obx,'NME','SO2',avtime='hourly')
#    make_stat_plots(stats,avstats,obx,'r2','PM25',avtime='24h')
