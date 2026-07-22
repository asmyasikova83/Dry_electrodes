import mne
import os
import numpy as np
import config as cfg
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

for subject in cfg.subjects:
    for headset in cfg.headsets_base:
        rec_data = []
        for recording in cfg.recordings_base:
            subject_headset = subject + '_' + headset
            extended_epochs_dir = os.path.join(cfg.epochs_dir, subject_headset)
            filename = f'{subject}_{headset}_{recording}_eeg.fif'
            path_fif = os.path.join(extended_epochs_dir, filename)
            print(path_fif)
            try:
                epochs = mne.read_epochs(path_fif, preload=True)

                data = epochs.get_data()  # (n_epochs, n_channels, n_times)
                rec_data.append(data)
                print('-----------------data shape', data.shape)
            except (OSError):
                print('This file not exist')

        # Усредняем каждую запись по эпохам (ось 0)
        averaged_per_file = [data.mean(axis=0) for data in rec_data]  # усредняем сначала эпохи внутри каждого датасета: axis=0
        try:
            # Объединяем вдоль новой оси (ось 0)
            stacked_data = np.stack(averaged_per_file, axis=0)
            mean_data = np.mean(stacked_data, axis=0)
        except ValueError:
             print('No data to stack')
        #average_and_save_evoked(epochs, averaged_per_file, subject, headset)

        evoked = mne.EvokedArray(
            data=mean_data,
            info=epochs.info,
            tmin=epochs.tmin,
            comment=f"{subject}_{headset}"
        )

        save_path_fif = os.path.join(cfg.evoked_dir, f'{subject}_{headset}_eeg.fif')
        evoked.save(save_path_fif, overwrite=True)

