import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Путь к данным
dir = r'\\MCSSERVER\DB Temp\physionet.org\files\dry_electrodes\epochs'
output_pics_dir = r"M:\DB Temp\physionet.org\files\dry_electrodes\epochs\pics"
os.makedirs(output_pics_dir, exist_ok=True)

# Переименования для типов гарнитур
headsets_mapping = {
    'active_new': 'DRY active + MCScap-DrA1 + SoftPulse™ Brush Flex',
    'active_old': 'DRY active + MCScap-DrA1 + SoftPulse™ Brush Medium',
    'passive_new': 'DRY + MCScap-DrP1 + датчики SoftPulse™ Brush Flex',
    'passive_old': 'DRY + MCScap-DrP1 + датчики SoftPulse™ Brush Medium',
    'wet': 'Мокрые'
}

# Порядок отображения гарнитур
headsets = ['wet', 'active_new', 'active_old', 'passive_new', 'passive_old']
display_headsets = [headsets_mapping[key] for key in headsets]

# Переименования для типов записей (задач)
recordings_mapping = {
    'eyes_open': 'Покой: глаза открыты',
    'eyes_closed': 'Покой: глаза закрыты',
    'cycling': 'Движение'
}
recordings_base = ['eyes_open', 'eyes_closed', 'cycling']
display_recordings = [recordings_mapping[key] for key in recordings_base]

subjects = ['S00', 'S01', 'S03', 'S04', 'S05']

# Создаём структуру для хранения данных
results = {}

for headset in headsets:
    results[headset] = {}
    for recording in recordings_base:
        share_artifact_rec = []
        for subject in subjects:
            # Формируем пути и имена
            filename_artifacts = f'{subject}_{headset}_{recording}_share_artifacts.txt'
            path_artifacts = os.path.join(dir, filename_artifacts)
            print(path_artifacts)

            share_artifacts = np.loadtxt(path_artifacts)
            share_artifact_rec.append(share_artifacts)

        # Сохраняем данные для текущей записи
        if share_artifact_rec:
            results[headset][recording] = share_artifact_rec

# Создаём DataFrame для анализа
data_for_analysis = []
for headset in results:
    for recording in results[headset]:
        values = results[headset][recording]
        for value in values:
            if not np.isnan(value):
                data_for_analysis.append({
                    'Headset': headset,
            'Recording': recording,
            'Share_Artifacts': value
        })

df = pd.DataFrame(data_for_analysis)

# Добавляем группировку по типам систем
def get_system_type(headset):
    if headset == 'wet':
        return 'Мокрая система'
    elif headset in ['active_new', 'active_old', 'passive_new', 'passive_old']:
        return 'Сухие системы'
    else:
        return 'Другие'

df['System_Type'] = df['Headset'].apply(get_system_type)

# Добавляем объединённую группу «Мокрая + сухие»
df_combined = df.copy()
df_combined['System_Type'] = 'Мокрая + сухие'

# Объединяем все данные
df_all = pd.concat([df, df_combined], ignore_index=True)

# Расчёт статистики по группам
grouped = df_all.groupby(['System_Type', 'Recording'])['Share_Artifacts'].agg(
    mean_artifacts='mean',
    std_artifacts='std',
    count='count'
).reset_index()

grouped['sem_artifacts'] = grouped['std_artifacts'] / np.sqrt(grouped['count'])

# Применяем маппинг названий записей
grouped['Recording'] = grouped['Recording'].map(recordings_mapping)

# Определяем порядок задач
recordings_order = display_recordings

# --- ГРАФИК 1: Мокрая система ---

wet_data = grouped[grouped['System_Type'] == 'Мокрая система']

means = []
stds = []

for recording in recordings_order:
    subset = wet_data[wet_data['Recording'] == recording]
    if not subset.empty:
        means.append(subset['mean_artifacts'].values[0])
        stds.append(subset['sem_artifacts'].values[0])
    else:
        means.append(0)
        stds.append(0)

fig1, ax1 = plt.subplots(figsize=(12, 8))
bars1 = ax1.bar(
    range(len(recordings_order)),
    means,
    yerr=stds,
    color='lightcoral',
    edgecolor='darkred',
    alpha=0.7,
    capsize=5,
    linewidth=1
)

ax1.set_ylabel('Средняя доля загрязнённых эпох (%)', fontsize=20)
#ax1.set_title('Мокрая система: распределение загрязнённых эпох по задачам', fontsize=18, fontweight='bold')
ax1.set_xticks(range(len(recordings_order)))
ax1.set_xticklabels(recordings_order, rotation=45, ha='right', fontsize=20)
ax1.set_ylim(0, 100)
ax1.tick_params(axis='y', labelsize=16)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Добавляем значения над столбцами
for bar, mean, std in zip(bars1, means, stds):
    if mean > 0:
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            mean,
            f'{mean:.1f}%',
            ha='center',
            va='bottom',
            fontsize=12,
            fontweight='bold',
            color='darkred'
        )

plt.tight_layout()
plt.savefig(os.path.join(output_pics_dir, 'wet_system_artifacts_distribution.svg'), dpi=300, bbox_inches='tight')
plt.close()

# --- ГРАФИК 2: Сухие системы ---
fig2, ax2 = plt.subplots(figsize=(12, 8))
dry_data = grouped[grouped['System_Type'] == 'Сухие системы']

means = []
stds = []

for recording in recordings_order:
    subset = dry_data[dry_data['Recording'] == recording]
    if not subset.empty:
        means.append(subset['mean_artifacts'].values[0])
        stds.append(subset['sem_artifacts'].values[0])
    else:
        means.append(0)
        stds.append(0)

bars2 = ax2.bar(
    range(len(recordings_order)),
    means,
    yerr=stds,
    color='lightblue',
    edgecolor='darkblue',
    alpha=0.7,
    capsize=5,
    linewidth=1
)

ax2.set_ylabel('Средняя доля загрязнённых эпох (%)', fontsize=20)
#ax2.set_title('Сухие системы: распределение загрязнённых эпох по задачам', fontsize=18, fontweight='bold')
ax2.set_xticks(range(len(recordings_order)))
ax2.set_xticklabels(recordings_order, rotation=45, ha='right', fontsize=20)
ax2.set_ylim(0, 100)
ax2.tick_params(axis='y', labelsize=16)
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# Добавляем значения над столбцами — исправлено: ax2.text() вместо ax1.text()
for bar, mean, std in zip(bars2, means, stds):
    if mean > 0:
        ax2.text(  # <-- ключевое исправление: ax2 вместо ax1
            bar.get_x() + bar.get_width() / 2,
            mean,  # позиция над столбцом с небольшим отступом
            f'{mean:.1f}%',
            ha='center',
            va='bottom',
            fontsize=12,
            fontweight='bold',
            color='darkblue'
        )

plt.tight_layout()
plt.savefig(os.path.join(output_pics_dir, 'dry_system_artifacts_distribution.svg'), dpi=300, bbox_inches='tight')
plt.close()

# --- ГРАФИК 3: Сухие системы ---
fig3, ax3 = plt.subplots(figsize=(12, 8))
dry_data = grouped[grouped['System_Type'] == 'Мокрая + сухие']

means = []
stds = []

for recording in recordings_order:
    subset = dry_data[dry_data['Recording'] == recording]
    if not subset.empty:
        means.append(subset['mean_artifacts'].values[0])
        stds.append(subset['sem_artifacts'].values[0])
    else:
        means.append(0)
        stds.append(0)

bars3 = ax3.bar(
    range(len(recordings_order)),
    means,
    yerr=stds,
    color='gray',
    edgecolor='darkgray',
    alpha=0.7,
    capsize=5,
    linewidth=1
)

ax3.set_ylabel('Средняя доля загрязнённых эпох (%)', fontsize=20)
ax3.set_xticks(range(len(recordings_order)))
ax3.set_xticklabels(recordings_order, rotation=45, ha='right', fontsize=20)
ax3.set_ylim(0, 100)
ax3.tick_params(axis='y', labelsize=16)
ax3.grid(axis='y', alpha=0.3, linestyle='--')

# Добавляем значения над столбцами — исправлено: ax2.text() вместо ax1.text()
for bar, mean, std in zip(bars3, means, stds):
    if mean > 0:
        ax3.text(  # <-- ключевое исправление: ax2 вместо ax1
            bar.get_x() + bar.get_width() / 2,
            mean,  # позиция над столбцом с небольшим отступом
            f'{mean:.1f}%',
            ha='center',
            va='bottom',
            fontsize=12,
            fontweight='bold',
            color='black'
        )

plt.tight_layout()
plt.savefig(os.path.join(output_pics_dir, 'all_system_artifacts_distribution.svg'), dpi=300, bbox_inches='tight')
plt.close()

