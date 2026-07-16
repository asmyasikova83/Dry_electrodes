import os
import mne
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import config as cfg
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

def detect_artifacts_threshold(epochs, threshold):
    """
    Detects artifacts using amp threshold.
    """
    data = epochs.get_data(copy=True)  # форма: (n_epochs, n_channels, n_times)

    # Проверяем абсолютную амплитуду по всем каналам и отсчётам
    max_amps = np.max(np.abs(data), axis=(1, 2))  # макс. амплитуда для каждой эпохи

    # Отмечаем эпохи, где макс. амплитуда > порога
    bad_epochs = max_amps > threshold
    check = max_amps[0] - threshold
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
    print('times', times)
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
    if aggtype == 'Headset' and rest == 0:
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
    if rest == 0:
        for bar, mean, sem in zip(bars, ordered_df['mean_artifacts'], ordered_df['sem_artifacts']):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                mean + grouped_by['sem_artifacts'].max() * 0.05,
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