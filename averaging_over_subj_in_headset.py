import mne
import os
import numpy as np
import config as cfg
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

headsets_base = cfg.headsets_base
subjects = ['S00', 'S01', 'S03', 'S04','S05']
evoked_dir = cfg.evoked_dir

for headset in headsets_base:
    subj_data = []
    for subject in subjects:
        subject_headset = subject + '_' + headset
        filename = f'{subject}_{headset}_eeg.fif'
        path_fif = os.path.join(cfg.evoked_dir, filename)
        print(path_fif)
        try:
            evokeds = mne.Evoked(path_fif)
            data = evokeds.get_data()  # ( n_channels, n_times)
            print('data.shape', data.shape)
            subj_data.append(data)
        except (OSError):
            print('This file not exist')

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
        comment=f"{headset}"
    )
    print(evoked)
    evoked_subj_dir = os.path.join(evoked_dir, headset)
    save_path_fif = os.path.join(evoked_dir, f'{headset}_eeg.fif')
    evoked.save(save_path_fif, overwrite=True)