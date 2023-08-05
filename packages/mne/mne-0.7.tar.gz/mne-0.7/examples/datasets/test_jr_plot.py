"""
========================================================
Decoding sensor space data with over time generalization
========================================================

The JR plot ...

"""
# Authors: Alexandre Gramfort <alexandre.gramfort@telecom-paristech.fr>
#
# License: BSD (3-clause)

print __doc__
import pylab as pl
import numpy as np

import mne
from mne import fiff

pl.close('all')

###############################################################################
# Set parameters
tmin, tmax = -0.3, 0.7
event_id = {"faces":1, "scrambled":2}

# raw_fname = 'SPM_CTF_MEG_example_faces1_3D_raw.fif'
# raw = fiff.Raw(raw_fname, preload=True)
# raw.filter(2, 45, method='iir')  # replace baselining with high-pass

raw_fname = 'SPM_CTF_MEG_example_faces1_3D_filt2-40_raw.fif'
raw = fiff.Raw(raw_fname)

# Setup for reading the raw data
events = mne.find_events(raw, stim_channel='UPPT001')
reject = dict(mag=1.5e-12)

# Read epochs
epochs = mne.Epochs(raw, events, event_id, tmin, tmax, proj=True,
                    picks=None, baseline=None, preload=True,
                    reject=reject)

epochs_list = [epochs[k] for k in event_id]
mne.epochs.equalize_epoch_counts(epochs_list)

###############################################################################
# Decoding in sensor space using a linear SVM
n_times = len(epochs.times)
# Take only the data channels (here the gradiometers)
data_picks = fiff.pick_types(epochs.info, meg=True, exclude='bads')
# Make arrays X and y such that :
# X is 3d with X.shape[0] is the total number of epochs to classify
# y is filled with integers coding for the class to predict
# We must have X.shape[0] equal to y.shape[0]
X = [e.get_data()[:, data_picks, :] for e in epochs_list]
y = [k * np.ones(len(this_X)) for k, this_X in enumerate(X)]
X = np.concatenate(X)
y = np.concatenate(y)

from sklearn.svm import SVC
from sklearn.metrics import SCORERS
from sklearn.cross_validation import StratifiedKFold

roc_auc_scorer = SCORERS['roc_auc']

clf = SVC(C=1, kernel='linear')
cv = StratifiedKFold(y, 5)

scores = np.zeros((n_times, n_times))

for train, test in cv:
    for t_train in xrange(n_times):
        X_train = X[train, :, t_train]
        # Standardize features
        mean, std = X_train.mean(axis=0), X_train.std(axis=0)
        X_train -= mean
        X_train /= std
        clf.fit(X_train, y[train])
        for t_test in xrange(n_times):
            X_test = X[test, :, t_test]
            X_test -= mean
            X_test /= std
            # scores[t_train, t_test] += clf.score(X_test, y)
            # Or using AUC score:
            scores[t_test, t_train] += roc_auc_scorer(clf, X_test, y[test])

scores /= len(cv)

times = 1e3 * epochs.times
scores *= 100  # make it percentage
pl.figure()
pl.imshow(scores, interpolation='nearest', origin='lower',
          extent=[times[0], times[-1], times[0], times[-1]],
          vmin=0., vmax=100.)
pl.xlabel('Times Test (ms)')
pl.ylabel('Times Train (ms)')
pl.title('Time generalization (%s vs. %s)' % tuple(event_id.keys()))
pl.axvline(0, color='k')
pl.axhline(0, color='k')
pl.colorbar()
pl.savefig('time_gen_%s_%s.pdf' % tuple(event_id.keys()))

pl.figure()
pl.plot(times, np.diag(scores), label="Classif. score")
pl.axhline(50, color='k', linestyle='--', label="Chance level")
pl.axvline(0, color='r', label='stim onset')
pl.legend()
pl.xlabel('Time (ms)')
pl.ylabel('Classification score')
pl.title('Decoding (%s vs. %s)' % tuple(event_id.keys()))
pl.savefig('decoding_%s_%s.pdf' % tuple(event_id.keys()))
pl.show()
