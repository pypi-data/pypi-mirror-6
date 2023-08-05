import mne
stc = mne.read_source_estimate('mne_dSPM_inverse-meg')
brain = stc.plot('sample', hemi='split', views=['lat', 'med'],
                 smoothing_steps=3, transparent=False,
                 time_label=None, fmin=-2, fmid=0, fmax=2,
                 colormap=mne.viz.mne_analyze_colormap([0, 1, 2]),
                 time_viewer=True)
