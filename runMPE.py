import glob
import mpe_stats as mpe
import make_plots as mp
import time
import os

start = time.time()
print('start')
os.system('mkdir -p ../figs')
# get cmaq and met files

#henry2
#cfiles = glob.glob('../../data_out/bc2014v3/d04/2014-01-0[1234567]/ \
# CCTM_D502a_Linux3_x86_64intel.ACONC.BOGOTA_bc2014v3_2014010[1234567].nc')
#mfiles = glob.glob('../../data_in/mcip/v4n/d04/METCRO2D_WRFd04v4n_2014-01-0[1234567]')

#macbook
cfiles = glob.glob('CCTM_D502a_Linux3_x86_64intel.ACONC.BOGOTA_bc2014v3_2014010[12].nc')
mfiles = glob.glob('METCRO2D_WRFd04v4n_2014-01-0[12]')
afiles = glob.glob('CCTM_D502a_Linux3_x86_64intel.AERODIAM.BOGOTA_bc2014v3_2014010[12].nc')

# Bezier
#cfiles = glob.glob('../../../data_out/bc2014v3/d04/2014-0[123]-??/CCTM_D502a_Linux3_x86_64intel.ACONC.BOGOTA_20140[123]??.nc')
#afiles = glob.glob('../../../data_out/bc2014v3/d04/2014-0[123]-??/CCTM_D502a_Linux3_x86_64intel.AERODIAM.BOGOTA_20140[123]??.nc')
#mfiles = glob.glob('../../../data_in/mcip/v4n/d04/METCRO2D_WRFd04v4n_2014-0[123]-??')
#cfiles = glob.glob('../../../data_out/bc2014v3/d04/2014-1?-??/CCTM_D502a_Linux3_x86_64intel.ACONC.BOGOTA_20141???.nc')
#afiles = glob.glob('../../../data_out/bc2014v3/d04/2014-1?-??/CCTM_D502a_Linux3_x86_64intel.AERODIAM.BOGOTA_20141???.nc')
#mfiles = glob.glob('../../../data_in/mcip/v4n/d04/METCRO2D_WRFd04v4n_2014-1?-??')
try:
    mfiles.remove('../../../data_in/mcip/v4n/d04/METCRO2D_WRFd04v4n_2014-12-31')
except:
    pass
#cfiles = glob.glob('../../data_out/bc2014v3/d04/2014-0[123]-??/CCTM_D502a_Linux3_x86_64intel.ACONC.BOGOTA_20140[123]??.nc')
#cfiles = glob.glob('../../data_out/bc2014v3/d04/2014-01-0[1234]/CCTM_D502a_Linux3_x86_64intel.ACONC.BOGOTA_2014010[1234].nc')
#mfiles = glob.glob('../../data_in/mcip/v4n/d04/METCRO2D_WRFd04v4n_2014-01-0[1234]')

cfiles.sort()
mfiles.sort()
afiles.sort()
#print(cfiles)
#print(mfiles)
#print(afiles)

# load files
fc = mpe.get_cmaq(cfiles, afiles)
fo = mpe.get_obs(season='OND')
fm = mpe.get_met(mfiles)
obx, modx, metx = mpe.pair_data(fo, fc, fm)
#print(modx.time)
print(obx.O3)
print(modx.O3)
stats = mpe.calc_stats(obx, modx)
#print(modx.time)

print('done!')
#print(stats)
#print(obx)
#print(metx)
#print(modx)
print('making plots')
# make plots
mpe.plot_stats( obx, modx )
#print(modx.time)

mpe.plot_scatter( obx, modx )
#print(modx.time)

print('plots done!!11!!1!!!!!!!')
end = time.time()
print(end - start)
