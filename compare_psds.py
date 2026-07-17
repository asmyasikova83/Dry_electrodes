import matplotlib.pyplot as plt
import numpy as np
import config as cfg
from functions import compute_psds, do_ttest, plot_spectra

recordings_base = cfg.recordings_base
headsets_base = cfg.headsets_base

headset = 0
if headset:
    base = headsets_base
    colors = plt.cm.tab10(np.linspace(0, 1, len(headsets_base)))
else:
    base = recordings_base
    colors = ['purple', 'magenta', 'red']

# PSDs
psds = compute_psds(base)

# Plots
freqs, psd_data_list = plot_spectra(psds, base, headset, colors)

# Statistical analysis
stat = 1
if stat:
    t_stats_all, p_values_all, significant_pvals, pvals_corrected, significant_freqs_all = do_ttest(base, psd_data_list, freqs)


