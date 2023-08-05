"""
===================================================================
Plot time-frequency representations on topographies for MEG sensors
===================================================================

Both induced power and phase locking values are displayed.
"""
print __doc__

# Authors: Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>
#
# License: BSD (3-clause)

import numpy as np
import pylab as pl
import mne
from mne import fiff
from mne.time_frequency import induced_power
from mne.layouts import read_layout
from mne.viz import plot_topo_power, plot_topo_phase_lock

###############################################################################
# Set parameters
raw_fname = 'SPM_CTF_MEG_example_faces%d_3D_raw.fif'

# Or just one:
raw = fiff.Raw(raw_fname % 1)

# FIX channel names in raw and layout

###############################################################################
layout = read_layout('CTF-275')
layout.names = [name.split('-')[0] for name in layout.names]

for c in raw.info['chs']:
    c['ch_name'] = c['ch_name'].split('-')[0]

raw.info['ch_names'] = [c['ch_name'] for c in raw.info['chs']]

events = mne.find_events(raw, stim_channel='UPPT001')

event_ids = {"faces":1, "scrambled":2}

tmin, tmax = -0.3, 1.6
baseline = (None, 0)
# baseline = None  # no baseline as high-pass is applied

reject = dict(mag=1.5e-12)
include = ['MRO11-2908']

picks = fiff.pick_types(raw.info, meg=True, eeg=False, eog=True,
                        stim=False, exclude='bads', include=include)
# picks = fiff.pick_types(raw.info, meg=False, eeg=False, eog=True,
#                         stim=False, exclude='bads', include=include)

epochs = mne.Epochs(raw, events, event_ids, tmin, tmax, proj=True,
                    baseline=baseline, reject=reject, picks=picks,
                    detrend=1)

data = epochs.get_data()  # as 3D matrix

###############################################################################
# Calculate power and phase locking value

# frequencies = np.arange(7, 30, 3)  # define frequencies of interest
# frequencies = np.arange(5, 120, 2)  # define frequencies of interest
frequencies = np.arange(25, 100, 2)  # define frequencies of interest
n_cycles = frequencies / float(4)  # different number of cycle per frequency
Fs = raw.info['sfreq']  # sampling in Hz
decim = 4
power, phase_lock = induced_power(data, Fs=Fs, frequencies=frequencies,
                                  n_cycles=n_cycles, n_jobs=1, use_fft=False,
                                  decim=decim, zero_mean=True)

times = epochs.times

# baseline corrections with ratio
baseline=(-0.15, 0)  # avoid edge effects
power = mne.baseline.rescale(power, times[::decim], baseline, mode='percent')

border_size = 15
power = power[:,:,border_size:-border_size]  # remove edges
phase_lock = phase_lock[:,:,border_size:-border_size]  # remove edges
times = times[::decim][border_size:-border_size]
                                  ###############################################################################
# View time-frequency plots

vmax = np.max(np.abs(power))
vmin = -vmax

# import pylab as pl
# pl.close('all')
# pl.figure()
# pl.imshow(power[0], extent=[times[0], times[-1],
#                                     frequencies[0], frequencies[-1]],
#         aspect='auto', origin='lower', vmin=vmin, vmax=vmax)
# pl.xlabel('Time (s)')
# pl.ylabel('Frequency (Hz)')
# pl.title('Induced power')
# pl.colorbar()
# 
# pl.figure()
# pl.imshow(phase_lock[0], extent=[times[0], times[-1],
#                             frequencies[0], frequencies[-1]],
#         aspect='auto', origin='lower')
# pl.xlabel('Time (s)')
# pl.ylabel('Frequency (Hz)')
# pl.title('Phase-lock')
# pl.colorbar()
# pl.show()

###############################################################################
# Show topography of power.
title = 'Induced power - SPM Face data'
plot_topo_power(epochs, power, frequencies, layout, decim=decim, mode=None,
                vmin=-.5, vmax=.5, title=title, dB=False)
pl.show()

###############################################################################
# Show topography of phase locking value (PLV)
title = 'Phase locking value - SPM Face data'
plot_topo_phase_lock(epochs, phase_lock, frequencies, layout, mode=None,
                     decim=decim, title=title)
pl.show()
