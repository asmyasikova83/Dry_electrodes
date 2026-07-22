import os
import mne
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from scipy.stats import ttest_rel
import config as cfg
import math
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

data_dir = cfg.data_dir
output_pics_dir = cfg.output_pics_dir

def artifacts_share_into_df(results):
    """
    Function to convert artitfacts share to pandas DataFrame
    """
    data_for_excel = []

    for headset in results:
        for recording in results[headset]:
            values = results[headset][recording]

            row = {
                'Headset': headset,
                'Recording': recording,
                'Mean_Share_Artifacts': np.nanmean(values),
                'Std_Share_Artifacts': np.nanstd(values),
                'N_Subjects': len([v for v in values if not np.isnan(v)])
            }

            for i, value in enumerate(values):
                row[f'Subject_{i + 1}'] = value

            data_for_excel.append(row)

    df = pd.DataFrame(data_for_excel)

    output_file = os.path.join(data_dir, 'share_artifacts_summary.xlsx')
    df.to_excel(output_file, index=False)
    print(f'Artifacts share saved: {output_file}')

    return df

def average_and_save_evoked(evokeds, subj_data, subject, avtype):
    """
    Function to calculate average over epochs and save evoked data
    """
    # TODO
    # Averaging over epochs (axis = 0)
    stacked_data = np.stack(subj_data, axis=0)
    mean_data = np.mean(stacked_data, axis=0)

    evoked = mne.EvokedArray(
        data=mean_data,
        info=evokeds.info,
        tmin=evokeds.tmin,
        comment=f'{subject}{avtype}'
    )
    evoked.nave = stacked_data.shape[0]
    save_path_fif = os.path.join(cfg.evoked_dir, f'{subject}{avtype}_eeg.fif')
    evoked.save(save_path_fif, overwrite=True)

def combine_rest_data(results):
    """
    Function to combine rest data: eyes open & eyes closed
    """
    combined_results = {}
    for headset in results:
        combined_results[headset] = {}
        # Combine eyes_open и eyes_closed
        rest_data = []
        for recording in ['eyes_open', 'eyes_closed']:
            if recording in results[headset]:
                rest_data.extend(results[headset][recording])
        rest_data_clean = [x for x in rest_data if not np.isnan(x)]
        if rest_data_clean:
            combined_results[headset]['rest'] = rest_data_clean
        if 'cycling' in results[headset]:
            combined_results[headset]['cycling'] = results[headset]['cycling']

    return combined_results

def compute_psds(base):
    """
    Function to compute psds
    """
    psds = []
    for i, b in enumerate(base):
        filename = f'{b}_eeg.fif'
        print(f'processing {filename}')
        path_fif = os.path.join(cfg.evoked_dir, filename)
        print(path_fif)
        try:
            evokeds = mne.read_evokeds(path_fif)[0]
            print(evokeds)

            evokeds_data = evokeds.get_data()
            evokeds_mean_data = np.mean(evokeds_data, axis=0)

            # Into (1, n_times)
            evokeds_mean_data_reshaped = evokeds_mean_data.reshape(1, -1)

            info_single_channel = mne.create_info(
                ch_names=['Average'],
                sfreq=evokeds.info['sfreq'],
                ch_types=['eeg']
            )

            evokeds_mean_ch = mne.EvokedArray(
                data=evokeds_mean_data_reshaped,
                info=info_single_channel,
                tmin=evokeds.tmin,
                comment=f"{b} Average Chan"
            )

            # Вычисляем PSD с ограничением по частоте
            psd = evokeds_mean_ch.compute_psd(fmin=cfg.fmin, fmax=cfg.fmax)
            psds.append(psd)

        except (OSError, FileNotFoundError):
            print(f'This file does not exist: {path_fif}')
            continue  # пропускаем, если файл не найден
        except Exception as e:
            print(f'Error reading {path_fif}: {e}')
            continue

    return psds

def detect_artifacts_diff(epochs, diff_threshold):
    """
    Обнаружение артефактов по разности между соседними отсчётами.
    """
    data = epochs.get_data(copy=True)
    n_epochs, n_channels, n_times = data.shape

    max_diffs = np.zeros(n_epochs)
    for i in range(n_epochs):
        epoch_data = data[i]
        diffs = np.diff(epoch_data, axis=1) # (n_channels, n_times-1)
        max_diff = np.max(np.abs(diffs))
        max_diffs[i] = max_diff
    bad_epochs = max_diffs > diff_threshold
    return bad_epochs, max_diffs

def detect_artifacts_threshold(epochs, threshold):
    """
    Detects artifacts using amp threshold.
    """
    data = epochs.get_data(copy=True)  # форма: (n_epochs, n_channels, n_times)

    # Проверяем абсолютную амплитуду по всем каналам и отсчётам
    max_amps = np.max(np.abs(data), axis=(1, 2))  # макс. амплитуда для каждой эпохи
    print('max_amps', max_amps)
    # Отмечаем эпохи, где макс. амплитуда > порога
    bad_epochs = max_amps > threshold
    check = max_amps[0] - threshold
    print(check)
    return bad_epochs, max_amps


def detect_artifacts_trend(epochs, trend_threshold):
    """
    Detects artifacts using linreg slope.
    """

    data = epochs.get_data(copy=True)
    n_epochs, n_channels, n_times = data.shape
    sfreq = epochs.info['sfreq']

    # Into s
    times = np.arange(n_times) / sfreq

    trends = np.zeros(n_epochs)

    for i in range(n_epochs):
        epoch_data = data[i]
        channel_trends = []
        for ch in range(n_channels):
            # Линейная регрессия: наклон — это коэффициент при x
            slope, _, _, _, _ = stats.linregress(times, epoch_data[ch])
            channel_trends.append(abs(slope))
        # Берём макс. наклон среди каналов
        trends[i] = np.max(channel_trends)

    # Отмечаем эпохи с наклоном > порога
    bad_epochs = trends > trend_threshold

    return bad_epochs, trends

def do_ttest(base, psd_data_list, freqs):
    """
    Function to perform ttest
    """
    print("\n" + "=" * 50)
    print("СТАТИСТИЧЕСКИЙ АНАЛИЗ: T‑ТЕСТ МЕЖДУ ГАРНИТУРАМИ")
    print("=" * 50)

    # Выбираем первую гарнитуру как контрольную 'wet'
    control_idx = 0
    control_name = base[control_idx]
    control_data = psd_data_list[control_idx]

    print(f"\nКонтрольная гарнитура: {control_name}")
    print(f"Сравниваем с остальными гарнитурами:\n")

    # Проводим t‑тест по всем частотам между контрольной и остальными гарнитурами
    t_stats_all = []
    p_values_all = []
    significant_freqs_all = []

    test_name = base
    test_data = np.vstack(psd_data_list)

    # T‑тест для каждой частоты (зависимые выборки)
    t_stats = []
    p_values = []
    control_data = control_data[np.newaxis]
    t_stat, p_val = ttest_rel(
            control_data,
            test_data,
            axis=0
    )
    t_stats.append(t_stat)
    p_values.append(p_val)
    p_values = np.squeeze(p_values)

    # p_values = p_values[np.newaxis]
    reject, pvals_corrected, _, _ = multipletests(
            p_values, alpha=0.05, method='fdr_bh'
    )

    significant_freqs = freqs[reject]
    significant_pvals = pvals_corrected[reject]

    t_stats_all.append(t_stats)
    p_values_all.append(pvals_corrected)
    significant_freqs_all.append(significant_freqs)

    print('significant_freqs_all', significant_freqs_all)

    return t_stats_all, p_values_all, significant_pvals, pvals_corrected, significant_freqs_all

def plot_trend_detection(epochs, epoch_idx, channel_idx=0):
    """Shows trend for each channel and epoch."""
    data = epochs.get_data(copy=True)
    epoch_data = data[epoch_idx, channel_idx, :]
    sfreq = epochs.info['sfreq']
    times = np.arange(len(epoch_data)) / sfreq  # время в секундах

    # Линейная регрессия
    slope, intercept, _, _, _ = stats.linregress(times, epoch_data)
    trend_line = slope * times + intercept  # уравнение прямой

    plt.figure(figsize=(10, 4))
    plt.plot(times, epoch_data * 1e6, label='EEG signal (muV)')  # в мкВ
    plt.plot(times, trend_line * 1e6, '--r', label=f'Trend (slope: {slope*1e6:.2f} muV/s)')
    plt.xlabel('Time, s')
    plt.ylabel('Amplitude, muV')
    plt.title(f'Epoch {epoch_idx}, channel {channel_idx}')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_share_artifacts(df, aggtype, mapping, base, rest):
    """
    Plots artifact share in % over recordings/headset type
    """
    os.makedirs(output_pics_dir, exist_ok=True)

    # Группировка и построение гистограмм по Recording
    # grouped_by_recording = df.groupby('Recording')[['Mean_Share_Artifacts', 'Std_Share_Artifacts']].mean()
    # Группировка и расчёт статистики по Headset
    grouped_by = df.groupby(aggtype)['Mean_Share_Artifacts'].agg(
        mean_artifacts='mean',
        std_artifacts='std',
        count='count'
    )

    # (SEM): SEM = σ / √n
    grouped_by['sem_artifacts'] = grouped_by['std_artifacts'] / np.sqrt(
        grouped_by['count'])
    grouped_by.index = grouped_by.index.map(mapping)

    ordered_data = []
    for b in base:
        full_name = mapping[b]
        if full_name in grouped_by.index:
            row = grouped_by.loc[full_name]
            ordered_data.append({
                'mean_artifacts': row['mean_artifacts'],
                'std_artifacts': row['std_artifacts'],
                'sem_artifacts': row['sem_artifacts']
            })
        else:
            ordered_data.append({
                'mean_artifacts': 0,
                'std_artifacts': 0,
                'sem_artifacts': 0
            })

    ordered_df = pd.DataFrame(ordered_data, index=[mapping[h] for h in base])

    # Histogram by Mean_Share_Artifacts для Recording
    fig, ax = plt.subplots(figsize=(16, 12))
    colors = ['lightblue', 'lightgreen', 'lightcoral', 'wheat', 'plum']

    if rest:
        recording = 'rest'
        mask = df['Recording'] == recording
        df_rest = df[mask]

        means = []
        stds = []
        sems = []
        labels = []
        for b in base:
            mask_headset = df_rest['Headset'] == b
            df_headset = df_rest[mask_headset]

            subject_columns = [col for col in df_headset.columns if col.startswith('Subject_')]
            values = df_headset[subject_columns].values.flatten()
            values_clean = values

            if len(values_clean) > 0:
                mean_val = np.mean(values_clean)
                std_val = np.std(values_clean, ddof=1)  # ddof=1 для несмещённой оценки
                sem_val = std_val / np.sqrt(len(values_clean))  # Стандартная ошибка среднего

                means.append(mean_val)
                stds.append(std_val)
                sems.append(sem_val)
                labels.append(mapping[b])

        bars = ax.bar(
            range(len(labels)),
            means,
            yerr=sems,
            color=colors[:len(labels)],
            edgecolor='darkblue',
            alpha=0.7,
            capsize=10,
            error_kw={
                'ecolor': 'black',
                'capsize': 10,
                'elinewidth': 3
            },
            linewidth=1
        )
        for bar, mean, sem in zip(bars, means, sems):
            if mean > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    mean + sem + max(sems) * 0.05,  # отступ от вершины уса
                    f'{mean:.1f}%',
                    ha='center',
                    va='bottom',
                    fontsize=20,
                    fontweight='bold',
                    color='darkblue'
                )
    if aggtype == 'Recording':
        bars = ax.bar(
            range(len(ordered_df)),
            ordered_df['mean_artifacts'],
            yerr=ordered_df['sem_artifacts'],
            color='skyblue',
            edgecolor='darkblue',
            alpha=0.7,
            capsize=5,
            linewidth=1
        )
    if aggtype == 'Headset' and rest != 1:
            bars = ax.bar(
                range(len(ordered_df)),
                ordered_df['mean_artifacts'],
                yerr=ordered_df['sem_artifacts'],
                color=colors[:len(ordered_df)],
                edgecolor='darkblue',
                alpha=0.7,
                capsize=5,
                linewidth=1
        )
    if rest != 1:
        for bar, mean, sem in zip(bars, ordered_df['mean_artifacts'], ordered_df['sem_artifacts']):
            if not math.isnan(sem):
                ax.text(
                bar.get_x() + bar.get_width() / 2,
                mean + grouped_by['sem_artifacts'].mean() + grouped_by['sem_artifacts'].max() * 0.05,
                f'{mean:.1f}%',
                ha='center',
                va='bottom',
                fontsize=20,
                fontweight='bold',
                color='darkblue'
                )
            else:
                ax.text(
                bar.get_x() + bar.get_width() / 2,
                mean,
                f'{mean:.1f}%',
                ha='center',
                va='bottom',
                fontsize=20,
                fontweight='bold',
                color='darkblue'
                )

    ax.set_ylim(0, 100)

    ax.set_ylabel('Средняя доля загрязнённых эпох (%)', fontsize=20)
    ax.set_xticks(range(len(ordered_df)))  # задаём позиции тиков
    ax.set_xticklabels(ordered_df.index, rotation=45, ha='right', fontsize=20)  # задаём подписи

    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.tick_params(axis='y', labelsize=11)

    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.tick_params(axis='y', labelsize=11)

    plt.tight_layout()

    plt.savefig(os.path.join(output_pics_dir, f'mean_artifacts_by_{aggtype}_rest_{rest}.svg'), dpi=300, bbox_inches='tight')
    plt.close()

    print(f'mean_artifacts_by_{aggtype}.svg saved in: {output_pics_dir}')

def plot_spectra(psds, base, headset, colors):
    """
    Function that plots spectra
    """
    # Создаём график для наложения всех спектров
    fig, ax = plt.subplots(figsize=(12, 8))

    # Список для хранения данных PSD в мкВ²/Гц
    psd_data_list = []

    # Draw spectra
    for i, psd in enumerate(psds):
        # Извлекаем частоты и данные PSD
        freqs = psd.freqs
        psd_data_V2_per_Hz = psd.get_data().squeeze()  # В²/Гц
        psd_data_uV2_per_Hz = psd_data_V2_per_Hz * 1e12  # мкВ²/Гц

        # Сохраняем данные для статистического анализа
        psd_data_list.append(psd_data_uV2_per_Hz)

        if headset:
            ax.plot(
                freqs,
                psd_data_uV2_per_Hz,
                label=cfg.display_headsets[i],
                color=colors[i],
                linewidth=2.0,
                alpha=0.9
            )
        else:
            ax.plot(
                freqs,
                psd_data_uV2_per_Hz,
                label=cfg.display_recordings[i],
                color=colors[i],
                linewidth=2.0,
                alpha=0.9
            )

    legend_ranges = [
        Line2D([0], [0], color=(0.2, 0.9, 0.6), alpha=0.3, lw=10, label='Альфа (8–12 Гц)'),
        Line2D([0], [0], color='gray', alpha=0.2, lw=10, label='Бета (13–30 Гц)')
    ]

    # ЗАЛИВКА ДИАПАЗОНОВ ЧАСТОТ (без label — чтобы не дублировать в легенде)
    ax.axvspan(8, 13, alpha=0.3, color=(0.2, 0.9, 0.6), label='_nolegend_')
    ax.axvspan(13, 30, alpha=0.2, color='gray', label='_nolegend_')

    # Создаём легенду для гарнитур (основная легенда)
    # Предположим, что линии графиков уже построены и имеют корректные метки
    legend_garnetures = ax.legend(
        fontsize=18,
        # title='Типы гарнитур',
        # title='Passive_Medium',
        title_fontsize=20,
        loc='upper right',  # расположение в левом верхнем углу
        frameon=True,
        fancybox=True,
        shadow=True
    )

    # Добавляем первую легенду обратно на график
    ax.add_artist(legend_garnetures)
    ax.set_yscale('log')
    # Настраиваем внешний вид графика
    # Добавляем легенду элементов к графику

    ax.set_xlabel('Гц', fontsize=18)
    ax.set_ylabel('Cпектральная плотность мощности (PSD)', fontsize=18)

    ax.set_xlim(cfg.fmin, cfg.fmax)  # ось X: от 1 до 40 Гц
    ax.set_ylim(0.01, 1000)  # ось Y: подберите под свои данные
    # Настраиваем формат меток: отображаем абсолютные значения
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(
        lambda val, pos: f'{val:.0f}' if val >= 1 else f'{val:.2f}'
    ))

    # Метки на осях (деления)
    ax.tick_params(axis='both', which='major', labelsize=18)

    # Добавляем сетку для лучшей читаемости
    ax.grid(True, alpha=0.3)

    # Обязательно добавляем первую легенду обратно через add_artist()
    ax.add_artist(legend_garnetures)

    plt.tight_layout()
    plt.show()

    # save_path = os.path.join(plots_dir, f'recordings_psd_averaged_5_passive_old.svg')
    save_path = os.path.join(output_pics_dir, f'spectra_{base}_psd_averaged_N{cfg.N}.svg')
    fig.savefig(save_path, dpi=cfg.dpi, bbox_inches='tight')
    print(f"Spectra plot is saved: {save_path}")

    return freqs, psd_data_list

def  read_artifacts(subjects, headsets_base, recordings_base):
    """
    Function to read artifacts from .txt and combine them in results
    """
    results = {}
    for headset in headsets_base:
        results[headset] = {}
        for recording in recordings_base:
            share_artifact_rec = []
            for subject in subjects:
                filename_artifacts = f'{subject}_{headset}_{recording}_share_artifacts.txt'
                path_artifacts = os.path.join(data_dir, filename_artifacts)
                print(path_artifacts)
                try:
                    share_artifacts = np.loadtxt(path_artifacts)
                    share_artifact_rec.append(share_artifacts)
                except (OSError, FileNotFoundError):
                    print(f'File not found: {path_artifacts}')
                    share_artifact_rec.append(np.nan)
            if share_artifact_rec:
                results[headset][recording] = share_artifact_rec

    return results