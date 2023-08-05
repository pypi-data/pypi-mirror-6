"""
====================================
Generate label from source estimates
====================================

Threshold a source estimate and produce a label after smoothing.

"""

# Author: Luke Bloy <luke.bloy@gmail.com>
#         Alex Gramfort <alexandre.gramfort@telecom-paristech.fr>
# License: BSD (3-clause)

import mne
from mne.minimum_norm import read_inverse_operator, apply_inverse
from mne.fiff import Evoked
import os
import pylab as pl
import numpy as np
from mne.stats.cluster_level import _find_clusters

def loadAparcLabel(labelName,subject=None,subjects_dir=None):
  if subject==None:
    if not os.environ.has_key('SUBJECT'):
      print "you must supply a subjectid or set the SUBJECT environment variable"
      return
    else:
      subject=os.environ['SUBJECT']
  #
  if subjects_dir==None:
    if not os.environ.has_key('SUBJECTS_DIR'):
      print "you must supply a subjects_dir or set the SUBJECTS_DIR environment variable"
      return
    else:
      subjects_dir=os.environ['SUBJECTS_DIR']
  #
  labels, label_colors = mne.labels_from_parc(subject, parc='aparc',subjects_dir=subjects_dir)
  label = None
  for tmp in labels:
    if tmp.name == labelName:
      label = tmp
      break
  if label == None:
    print "Can't find %s"%labelName
    return
  return label

def generateFunctionalLabel(totStc, aparcLabelName, src, subject, subjects_dir=None, percThresh=0.2, smoothing=1, subjects_dir=None):
  #ok we want to find a cluster centered on the max Power in aparcLabelName
  print "loadAparcLabel(%s,%s,%s)"%(aparcLabelName,subject,subjects_dir)
  tmpLabel = loadAparcLabel(aparcLabelName,subject=subject,subjects_dir=subjects_dir)

  tmpLabel_stc = totStc.in_label(tmpLabel)
  
  #ok we want the max vertex so we can look find it in the totData...
  totMax_tmp  = tmpLabel_stc.data.max()
  totMax_ind  = tmpLabel_stc.data.argmax()
  
  if totMax_ind < len(tmpLabel_stc.vertno[0]):
    totMax_vert = tmpLabel_stc.vertno[0][totMax_ind]
  else:
    totMax_vert = tmpLabel_stc.vertno[1][ totMax_ind - len(tmpLabel_stc.vertno[0]) ]

  #find the index in totStc.data the corresponds to totMax_vert...
  if totMax_vert in totStc.vertno[0]:
    totMaxIndex = np.nonzero(totMax_vert == totStc.vertno[0])[0][0]
  elif totMax_vert in totStc.vertno[1]:
    totMaxIndex = len(totStc.vertno[0]) + np.nonzero(totMax_vert == totStc.vertno[1])[0][0]
  else:
    print "Error finding vertexs"
    return
    
  #lets make sure the we found what we though we did...
  if (totStc.data[totMaxIndex,0] != totMax_tmp):
    print "Big Problems finding correct index"
    return

  src_conn = mne.spatial_src_connectivity(src)

  #what should we use as the threshold for seperating clusters
  thresh = percThresh * totMax_tmp
  clusters,sums = _find_clusters(totStc.data[:,0], thresh, connectivity=src_conn)

  #find the cluster with the totMaxVertex in it.
  bCluster = None
  for c in clusters:
    if totMaxIndex in c:
      bCluster = c
      break
  if (bCluster == None):
    print "clustering didn't work!"
    return
  
  #make a label from bCluster
  tmpData = np.zeros(totStc.data.shape)
  tmpData[bCluster] = 1
  tmpStc = mne.SourceEstimate( tmpData,vertices=totStc.vertno, tmin=0, tstep=1000, subject=subject)
  funcLabel = mne.stc_to_label(tmpStc, src=src, smooth=smoothing, subjects_dir=subjects_dir)[0]
  return funcLabel


from mne.datasets import sample

data_path = sample.data_path()
subjects_dir = data_path + '/subjects'
fname_inv = data_path + '/MEG/sample/sample_audvis-meg-oct-6-meg-inv.fif'
fname_evoked = data_path + '/MEG/sample/sample_audvis-ave.fif'
subjects_dir = data_path + '/subjects'
subject = 'sample'

snr = 3.0
lambda2 = 1.0 / snr ** 2
method = "dSPM"  # use dSPM method (could also be MNE or sLORETA)

# The purpose of this example is to show how to compute labels based on seed growing activity.
# we'll compute an ROI based on the peak power between 80 and 120 ms.
# and we'll use the bankssts-lh as the anatomical seed ROI
aparcLabelName = 'bankssts-lh'
tmin, tmax = 0.080, 0.120

# Load data
evoked = Evoked(fname_evoked, setno=0, baseline=(None, 0))
inverse_operator = read_inverse_operator(fname_inv)
src = inverse_operator['src']

# Compute inverse solution
stc = apply_inverse(evoked, inverse_operator, lambda2, method,
                    pick_normal=True)

# Make a summary stc file with total power between tmin and tmax.
totData = np.zeros((stc.data.shape[0],1))
totData[:,0] = np.abs(stc.data[:,(stc.times>tmin) & ( stc.times<tmax)].sum(1))
totStc = mne.SourceEstimate(totData,vertices=stc.vertno, tmin=0, tstep=1000, subject=subject)

# use the totStc to generate a functional label
# region growing is halted at 60% of the peak value (of totStc) within the anatomical roi specified by aparcLabelName
funcLabel = generateFunctionalLabel(totStc,aparcLabelName,src,subject,percThresh=0.6,smoothing=5,subjects_dir=subjects_dir)
funcLabel.name = "%s_%s"%('Active',aparcLabelName)

# load the anatomical ROI for comparison
anatLabel = loadAparcLabel(aparcLabelName,subject=subject,subjects_dir=subjects_dir)

# Plot brain in 3D with PySurfer if available. Note that the subject name
# is already known by the SourceEstimate stc object.
brain = totStc.plot(surface='inflated', hemi='lh', subjects_dir=subjects_dir)
brain.scale_data_colormap(fmin=0, fmid=350, fmax=700, transparent=True)
brain.show_view('lateral')

# show both labels --- requires the pysurfer develeper tree
#                      Other wise save to file and load from file.
brain.add_label(anatLabel, borders=True, color='k')
brain.add_label(funcLabel, borders=True, color='b')

#extract the anatomical time course for each label
stc_AnatLabel = stc.in_label(anatLabel)
pcaAnat = stc.extract_label_time_course(anatLabel, src, mode='pca_flip').flatten()

stc_FuncLabel = stc.in_label(funcLabel)
pcaFunc = stc.extract_label_time_course(funcLabel, src, mode='pca_flip').flatten()

#flip the pca so that the total power between tmin and tmax is positive
pcaAnat = (pcaAnat * np.sign(pcaAnat[ (stc_AnatLabel.times>tmin) & (stc_AnatLabel.times<tmax) ].sum()))
pcaFunc = (pcaFunc * np.sign(pcaFunc[ (stc_FuncLabel.times>tmin) & (stc_FuncLabel.times<tmax) ].sum()))

#plot the time courses....
pl.plot(1e3 * stc_AnatLabel.times,pcaAnat, 'k', label='Anatomical %s'%aparcLabelName)
pl.plot(1e3 * stc_FuncLabel.times,pcaFunc, 'b', label='Active %s'%aparcLabelName)
pl.legend()
pl.show()

