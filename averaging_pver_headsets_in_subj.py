import mne
import os
import numpy as np
import config as cfg
from functions import average_and_save_evoked
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

for subject in cfg.subjects:
    for recording in cfg.recordings_base:
        headset_data = []
        for headset in cfg.headsets_base:
            subject_headset = subject + '_' + headset
            extended_epochs_dir = os.path.join(cfg.epochs_dir, subject_headset)
            filename = f'{subject}_{headset}_{recording}_eeg.fif'
            path_fif = os.path.join(extended_epochs_dir, filename)
            try:
                epochs = mne.read_epochs(path_fif, preload=True)
                data = epochs.get_data()  # (n_epochs, n_channels, n_times)
                headset_data.append(data)

            except (OSError):
                print('This file not exist')

        # Усредняем каждую запись по эпохам (ось 0)
        averaged_per_file = [data.mean(axis=0) for data in headset_data]  # каждый элемент — (4, 1001)
        #average_and_save_evoked(epochs, headset_data.mean(axis=0), subject, headset)
        
        try:
            # Объединяем вдоль новой оси (ось 0)
            stacked_data = np.stack(averaged_per_file, axis=0)
            mean_data = np.mean(stacked_data, axis=0)
            
        except ValueError:
             print('No data to stack')
        
        # Создаём объект Evoked для сохранения
        evoked = mne.EvokedArray(
            data=mean_data,
            info=epochs.info,
            tmin=epochs.tmin,
            comment=f"{subject}_{headset}"
        )

        save_path_fif = os.path.join(cfg.evoked_dir, f'{subject}_{recording}_eeg.fif')
        evoked.save(save_path_fif, overwrite=True)
