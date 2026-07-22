import mne
import numpy as np
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

    #average_and_save_evoked(evokeds, subj_data, [], recording)

    # (5, 4, 1001) - 5 subjects, 5 chans, 1001 times
    stacked_data = np.stack(subj_data, axis=0)
    print('stacked_data.shape', stacked_data.shape)

    # (5, 4, 1001) - 5 subjects, 5 chans, 1001 times --> (4, 1001)
    mean_data = np.mean(stacked_data, axis=0)
    print('mean_data.shape', mean_data.shape)

    # Создаём объект Evoked для сохранения
    evoked = mne.EvokedArray(
        data=mean_data,
        info=evokeds.info,
        tmin=evokeds.tmin,
        comment=f"{recording}"
    )
    evoked_subj_dir = os.path.join(cfg.evoked_dir, recording)
    save_path_fif = os.path.join(cfg.evoked_dir, f'{recording}_eeg.fif')
    evoked.save(save_path_fif, overwrite=True)