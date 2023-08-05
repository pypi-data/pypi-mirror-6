"""
====================================
A full pipeline on SPM face contrast
====================================

Find events from the stimulation/trigger channel in the raw data.
"""
# Author: Alexandre Gramfort <alexandre.gramfort@telecom-paristech.fr>
#
# License: BSD (3-clause)

import mne
from mne import fiff

###############################################################################
# Set parameters
raw_fname = 'SPM_CTF_MEG_example_faces%d_3D_raw.fif'

# Or just one:
raw = fiff.Raw(raw_fname % 1, preload=True)

raw.filter(1, 45, method='iir')

events = mne.find_events(raw, stim_channel='UPPT001')

event_ids = {"faces":1, "scrambled":2}

tmin, tmax = -0.2, 0.7
baseline = None  # no baseline as high-pass is applied
reject = dict(mag=1.5e-12)

epochs = mne.Epochs(raw, events, event_ids, tmin, tmax, proj=True,
                    baseline=baseline, preload=True, reject=reject)
evoked = [epochs[k].average() for k in event_ids]
noise_cov = mne.compute_covariance(epochs.crop(None, 0))
noise_cov.save('noise-cov.fif')
mne.fiff.write_evoked('evoked-ave.fif', evoked)

import pylab as pl
pl.close('all')

for e in evoked:
    pl.figure()
    e.plot()

pl.show()