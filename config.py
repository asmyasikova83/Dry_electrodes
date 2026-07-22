import numpy as np
import os

# Dirs
project_dir  = r'\\MCSSERVER\DB Temp\msasha\Dry_EEG'
epochs_artifacts_dir = r'\\MCSSERVER\DB Temp\msasha\Dry_EEG\epochs\artifacts'
spectra_dir = r'\\MCSSERVER\DB Temp\msasha\Dry_EEG\epochs\spectra_pic'
evoked_dir = r'\\MCSSERVER\DB Temp\msasha\Dry_EEG\evoked'
epochs_dir  = r'\\MCSSERVER\DB Temp\msasha\Dry_EEG\epochs'
output_pics_dir = r'\\MCSSERVER\DB Temp\msasha\Dry_EEG\epochs\pics'
output_path_random_table = r'C:\Users\msasha\Desktop\dry_electrodes\Эксперимент\experiment_data_day_{}.xlsx'
os.makedirs(epochs_artifacts_dir, exist_ok=True)
os.makedirs(spectra_dir, exist_ok=True)
os.makedirs(evoked_dir, exist_ok=True)
os.makedirs(output_pics_dir, exist_ok=True)
os.makedirs(output_pics_dir, exist_ok=True)

# Rename headsets
headsets_mapping = {
    'active_new': 'DRY active + MCScap-DrA1 + Brush Flex ',
    'active_old': 'DRY active + MCScap-DrA1 + Brush Medium',
    'passive_new': 'DRY + MCScap-DrP1 + Brush Flex',
    'passive_old': 'DRY + MCScap-DrP1 + Brush Medium',
    'wet': 'Мокрые'
}
headsets_base = ['wet', 'active_new', 'active_old', 'passive_new', 'passive_old']
display_headsets = [headsets_mapping[key] for key in headsets_base]
recordings_base = ['eyes_open', 'eyes_closed', 'cycling']

# Rename recordings
recordings_mapping = {
    'eyes_open': 'Покой: глаза открыты',
    'eyes_closed': 'Покой: глаза закрыты',
    'cycling': 'Движение'
    }
display_recordings = [recordings_mapping[key] for key in recordings_base]
subjects = ['S00', 'S01', 'S03', 'S04', 'S05']

# Plots
dpi = 300

N = 5

# Artifacts
fmin = 0.5
fmax = 40
filter_type = 'firwin'
fir_window = 'hamming'
sampling_rate = 500
duration = 2.0  # s
overlap = 0.5
time = np.arange(0, duration, 1 / sampling_rate)
n_fft = int(2 * sampling_rate)  # n_fft fot frequency resolution of 0.5 Hz
AMP_THRESHOLD = 80e-6  # 80 мкВ в вольтах
TREND_THRESHOLD = 10e-6   # 10 мкВ/с в вольтах/с
DIFF_THRESHOLD = 25e-6    # 25 мкВ в вольтах

#  List of channels to keep
channels_of_interest = [
    "F3-F4", "C3-C4", "P3-P4", "T5-T6"
]
