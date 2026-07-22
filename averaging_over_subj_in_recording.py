import mne
import os
import config as cfg
from functions import average_and_save_evoked
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

for recording in cfg.recordings_base:
    subj_data = []
    for subject in cfg.subjects:
        filename = f'{subject}_{recording}_eeg.fif'
        path_fif = os.path.join(cfg.evoked_dir, filename)
        try:
            evokeds = mne.Evoked(path_fif)
            data = evokeds.get_data()  # (n_epochs, n_channels, n_times)
            subj_data.append(data)
        except (OSError):
            print('This file not exist')

    average_and_save_evoked(evokeds, subj_data, recording)