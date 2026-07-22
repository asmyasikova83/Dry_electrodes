# Dry_electrodes
Dry EEG active / passive + types of sensors Brush Flex / Brush Medium

0.randomize_sessions_in_table.py  -- creates a data table with randomized experimental sessions for subjects

1.epoching_and_processing.py  -- does the preprocessing with data cleaning

2.compute_plot_artifacts_share.py -- plots share of artifacts in headsets and recording types

3.averaging_over_recordings_in_subj.py (f'{subject}_{headset}_eeg.fif') --> averaging_over_subj_in_headset.py (f'{headset}_eeg.fif') --> headset = 1 in compute_psds.py

4.averaging_pver_headsets_in_subj.py  (f'{subject}_{recording}_eeg.fif') --> averaging_over_subj_in_recording.py (f'{recording}_eeg.fif') --> headset = 0 in compute_psds.py

5.compare_psds.py -- plots spectra of headsets / recording types

## requirements!