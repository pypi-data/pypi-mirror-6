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
from mne.datasets import sample

data_path = sample.data_path()

pl.close('all')

###############################################################################
# Set parameters
raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'
event_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw-eve.fif'
tmin, tmax = -0.2, 0.5
event_id = dict(vis_l=3, vis_r=4)
# event_id = dict(aud_l=1, aud_r=2)
# event_id = dict(aud_l=1, vis_l=3)
# event_id = dict(aud_r=1, vis_r=3)

# Setup for reading the raw data
raw = fiff.Raw(raw_fname, preload=True)
raw.filter(2, 20, method='iir')  # replace baselining with high-pass
events = mne.read_events(event_fname)

event_id = dict(auditory=1, visual=2)
events = mne.merge_events(events, [1, 2], 1)
events = mne.merge_events(events, [3, 4], 2)

# Set up pick list: EEG + MEG - bad channels (modify to your needs)
raw.info['bads'] += ['MEG 2443', 'EEG 053']  # bads + 2 more
picks = fiff.pick_types(raw.info, meg='grad', eeg=False, stim=True, eog=True,
                        exclude='bads')

# Read epochs
epochs = mne.Epochs(raw, events, event_id, tmin, tmax, proj=True,
                    picks=picks, baseline=None, preload=True,
                    reject=dict(grad=4000e-13, eog=150e-6))

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
from sklearn.cross_validation import StratifiedKFold, StratifiedShuffleSplit

roc_auc_scorer = SCORERS['roc_auc']

clf = SVC(C=1, kernel='linear')
# cv = StratifiedKFold(y, 5)
cv = StratifiedShuffleSplit(y, 10, test_size=0.2)

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
