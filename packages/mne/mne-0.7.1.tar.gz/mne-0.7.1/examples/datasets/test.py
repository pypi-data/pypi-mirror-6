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

layout = read_layout('CTF-275')
