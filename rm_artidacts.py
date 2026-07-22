import config as cfg
from functions import (make_names, preprocessing, write_num_epochs, detect_and_remove_bad_epochs,
                       write_num_artifacts, write_share_artifacts, plot_subject_psd,
                       add_annotations_to_epochs, save_epochs_in_fif)
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

for headset in cfg.headsets_base:
    for recording in cfg.recordings_base:
        for subject in cfg.subjects:

            full_path,dir_name = make_names(subject, headset, recording)
            epochs, events = preprocessing(full_path)
            num_epochs = write_num_epochs(events, subject, headset, recording)
            bad_indices, epochs  = detect_and_remove_bad_epochs(epochs)
            num_artifacts = write_num_artifacts(bad_indices, subject,headset, recording)
            share_artifacts = write_share_artifacts(num_epochs, num_artifacts, subject, headset, recording)
            try:
                interactive = 0
                plot_subject_psd(interactive, epochs, subject, headset, recording)

                epochs = add_annotations_to_epochs(epochs)
                save_epochs_in_fif(epochs, subject, headset, recording)

            except RuntimeError as e:
                print("✗ No data left - after artifacts cleaning!")
