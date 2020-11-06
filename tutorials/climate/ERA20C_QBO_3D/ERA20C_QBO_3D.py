import os
import sys
import xarray as xr
import numpy  as np
from pathlib import Path

# Import library specific modules
sys.path.append("../../../")
from pyspod.spod_low_storage import SPOD_low_storage
from pyspod.spod_low_ram     import SPOD_low_ram
from pyspod.spod_streaming   import SPOD_streaming
import pyspod.weights as weights

# Current path
CWD = os.getcwd()

# Inspect and load data
file = os.path.join(CWD,'E20C_MONTHLYMEAN00_1900_2010_U131128_3D.nc')
ds = xr.open_dataset(file)
print(ds)

# we extract time, longitude and latitude
t = np.array(ds['time'])
x1 = np.array(ds['longitude'])
x2 = np.array(ds['latitude'])
x3 = np.array(ds['level'])
print('shape of t (time): ', t.shape)
print('shape of x1 (longitude): ', x1.shape)
print('shape of x2 (latitude) : ', x2.shape)
print('shape of x3 (level)    : ', x3.shape)

# we set the variables we want to use for the analysis
# (we select all the variables present) and load the in RAM
variables = ['u']
X = np.empty([t.shape[0], x1.shape[0], x2.shape[0], x3.shape[0], len(variables)])
for i,var in enumerate(variables):
    X[...,i] = np.einsum('tijk->tkji', np.array(ds[var]))
    X[...,i] = np.nan_to_num(X[...,i])
print('shape of data matrix X: ', X.shape)

# define required and optional parameters
params = dict()

# required parameters
params['dt'          ] = 744 # data time-sampling
params['nt'          ] = t.shape[0] # number of time snapshots
params['xdim'        ] = X[0,...,0].ndim   # number of spatial dimensions (longitude and latitude)
params['nv'          ] = len(variables)            # number of variables
params['n_FFT'       ] = np.ceil(12 * 12)          # length of FFT blocks
params['n_freq'      ] = params['n_FFT'] / 2 + 1  # number of frequencies
params['n_overlap'   ] = np.ceil(params['n_FFT'] * 0 / 100) # dimension block overlap region
params['mean'        ] = 'longtime'  # type of mean to subtract to the data
params['normalize'   ] = False        # normalization of weights by data variance
params['savedir'     ] = os.path.join(CWD, 'results', Path(file).stem) # folder where to save results
params['weights'] = weights.geo_weights_trapz_3D(\
    lat=x2,
    lon=x1,
    R=1,
    z=x3,
    n_vars=params['nv']) # weights

# optional parameters
params['savefreqs'   ] = np.arange(0,params['n_freq']) # frequencies to be saved
params['n_modes_save'] = 5      # modes to be saved
params['normvar'     ] = False  # normalize data by data variance
params['conf_level'  ] = 0.95   # calculate confidence level
params['savefft'     ] = False  # save FFT blocks to reuse them in the future (saves time)


# Perform SPOD analysis using low storage module
SPOD_analysis = SPOD_low_ram(X=X, params=params, data_handler=False, variables=variables)
spod = SPOD_analysis.fit()

# Show results
T_approx = 744 # approximate period (in days)
freq_found, freq_idx = spod.find_nearest_freq(freq_required=1/T_approx, freq=spod.freq)
modes_at_freq = spod.get_modes_at_freq(freq_idx=freq_idx)

freq = spod.freq*24
spod.plot_eigs()
spod.plot_eigs_vs_frequency(freq=freq)
spod.plot_eigs_vs_period   (freq=freq, xticks=[1, 7, 30, 365, 740, 1825])
spod.plot_3D_modes_slice_at_frequency(
    freq_required=freq_found,
    freq=freq,
    x1=x1-180,
    x2=x2,
    x3=x3,
    slice_dim=2,
    slice_id=2,
    coastlines='centred', modes_idx=[0,1,2], vars_idx=[0])
spod.plot_mode_tracers(
    freq_required=freq_found,
    freq=freq,
    coords_list=[(100,0,2)],
    modes_idx=[0,1,2])
spod.plot_data_tracers(coords_list=[(100,0,2),(200,10,10)])

