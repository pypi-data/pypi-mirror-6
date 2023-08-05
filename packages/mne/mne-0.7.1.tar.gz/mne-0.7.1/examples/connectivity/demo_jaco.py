"""
===============================================
Compute all-to-all connectivity in sensor space
===============================================

"""

# Author: Alexandre Gramfort <alexandre.gramfort@telecom-paristech.fr>
#
# License: BSD (3-clause)

import pylab as pl
import numpy as np

from mne.connectivity import spectral_connectivity

n_channels, n_times, n_epochs = 256, 200, 600
sfreq = 250.  # Hz
data = np.random.randn(n_epochs, n_channels, n_times)
# bands = dict(delta=(0, 4), theta=(4,8), alpha=(8,13), beta1=(13,20), beta2=(20,30), gamma=(30,45))
bands = dict(delta=(0, 4))

n_jobs = 2  # set it to 1 for single core and -1 for all cores

pl.close('all')

# for band_name, (fmin, fmax) in bands.iteritems():
#     for d in data:
#         (con_pli, con_plv, con_coh), freqs, times, n_epochs, n_tapers = \
#             spectral_connectivity(d[None, ...],
#                         method=['pli', 'plv', 'coh'], mode='multitaper', sfreq=sfreq,
#                         fmin=fmin, fmax=fmax, faverage=True,
#                         mt_adaptive=False, n_jobs=n_jobs)

for band_name, (fmin, fmax) in bands.iteritems():
    (con_pli, con_plv, con_coh), freqs, times, n_epochs, n_tapers = \
        spectral_connectivity(data,
                    method=['pli', 'plv', 'coh'], mode='multitaper', sfreq=sfreq,
                    fmin=fmin, fmax=fmax, faverage=True,
                    mt_adaptive=False, n_jobs=n_jobs)


from mne.time_frequency import multitaper_psd

psd, freqs = multitaper_psd(d[0], sfreq=sfreq)

#     pl.figure()
#     pl.subplot(1, 3, 1)
#     pl.imshow(con_pli[:, :, 0], interpolation='nearest')
#     pl.title("PLI")
#     pl.colorbar()
#     pl.subplot(1, 3, 2)
#     pl.imshow(con_plv[:, :, 0], interpolation='nearest')
#     pl.title("PLV")
#     pl.colorbar()
#     pl.subplot(1, 3, 3)
#     pl.imshow(con_coh[:, :, 0], interpolation='nearest')
#     pl.title("coherence")
#     pl.colorbar()
# 
#     pl.suptitle(band_name)
# 
# pl.show()