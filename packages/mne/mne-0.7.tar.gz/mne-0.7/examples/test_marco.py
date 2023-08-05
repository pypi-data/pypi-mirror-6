# Authors: Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>
#          Denis A. Engemann <d.engemann@fz-juelich.de>
#
# License: BSD (3-clause)

print __doc__

import mne
from mne import fiff
from mne.datasets import sample
data_path = sample.data_path()

###############################################################################
# Set parameters
raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'
event_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw-eve.fif'
event_id, tmin, tmax = 1, -0.2, 0.5

#   Setup for reading the raw data
raw = fiff.Raw(raw_fname)
events = mne.read_events(event_fname)

#   Set up pick list: EEG + STI 014 - bad channels (modify to your needs)
include = []  # or stim channels ['STI 014']
raw.info['bads'] = ['MEG 2443', 'EEG 053']

# pick EEG channels
picks = fiff.pick_types(raw.info, meg='grad', eeg=False, stim=False, eog=True,
                        include=include, exclude='bads')
# Read epochs
epochs = mne.Epochs(raw, events, event_id, tmin, tmax, picks=picks,
                    baseline=(None, 0), reject=dict(grad=2000e-13, eog=150e-6))

evoked = epochs.average()  # average epochs and get an Evoked dataset.

###############################################################################
# View evoked response
evoked.plot()

idx = 97
data = epochs.get_data()[:, idx, :]

from scipy import io
io.savemat('meg_one_sensor.mat', dict(data=data, times=evoked.times))
