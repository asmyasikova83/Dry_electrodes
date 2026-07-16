import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from functions import combine_rest_data

dir = r'\\MCSSERVER\DB Temp\physionet.org\files\dry_electrodes\epochs'

# Переименования для типов гарнитур
headsets_mapping = {
    'active_new': 'DRY active + MCScap-DrA1 + Brush Flex',
    'active_old': 'DRY active + MCScap-DrA1 + Brush Medium',
    'passive_new': 'DRY + MCScap-DrP1 + Brush Flex',
    'passive_old': 'DRY + MCScap-DrP1 + Brush Medium',
    'wet': 'Мокрые'
}

# Порядок отображения гарнитур
headsets = ['wet', 'active_new', 'active_old', 'passive_new', 'passive_old']
display_headsets = [headsets_mapping[key] for key in headsets]

# Типы записей — оставляем только rest
recordings_base = ['rest']

# Переименования для типов записей
recordings_mapping = {
    'rest': 'Покой (объединённый)'
}

display_recordings = [recordings_mapping[key] for key in recordings_base]

subjects = ['S00', 'S01', 'S03', 'S04', 'S05']

# Создаём структуру для хранения данных
results = {}

for headset in headsets:
    results[headset] = {}
    share_artifact_headset = []

    for recording in ['eyes_open', 'eyes_closed', 'cycling']:  # читаем исходные данные
        share_artifact_rec = []

        for subject in subjects:
            # Формируем пути и имена
            filename_artifacts = f'{subject}_{headset}_{recording}_share_artifacts.txt'
            path_artifacts = os.path.join(dir, filename_artifacts)
            print(path_artifacts)

            try:
                share_artifacts = np.loadtxt(path_artifacts)
                share_artifact_rec.append(share_artifacts)
            except (OSError, FileNotFoundError):
                print(f'Файл не найден: {path_artifacts}')
                share_artifact_rec.append(np.nan)  # Заменяем отсутствующие данные на NaN

        # Сохраняем данные для текущей записи
        if share_artifact_rec:
            results[headset][recording] = share_artifact_rec
            share_artifact_headset.append(np.nanmean(share_artifact_rec))  # Среднее по субъектам


# Объединяем данные для rest
combined_results = combine_rest_data(results)

# Создаём DataFrame для Excel
data_for_excel = []

for headset in combined_results:
    for recording in combined_results[headset]:
        # Берём данные для этой комбинации headset/recording
        values = combined_results[headset][recording]
        print('values', values)
        # Создаём строку для каждой комбинации
        row = {
            'Headset': headset,
            'Recording': recording,
            'Mean_Share_Artifacts': np.nanmean(values),
            'Std_Share_Artifacts': np.nanstd(values, ddof=1),
            'N_Subjects': len([v for v in values if not np.isnan(v)])
        }
        # Добавляем индивидуальные значения по субъектам (если нужно)
        for i, value in enumerate(values):
            row[f'Subject_{i+1}'] = value
        data_for_excel.append(row)

# Преобразуем в DataFrame
df = pd.DataFrame(data_for_excel)

print(df)

# Сохраняем в Excel
output_file = os.path.join(dir, 'share_artifacts_summary.xlsx')
df.to_excel(output_file, index=False)
print(f'Результаты сохранены в файл: {output_file}')

# Путь для сохранения изображений
output_pics_dir = r"M:\DB Temp\physionet.org\files\dry_electrodes\epochs\pics"
os.makedirs(output_pics_dir, exist_ok=True)

# Цвета для столбцов
colors = ['lightblue', 'lightgreen', 'lightcoral', 'wheat', 'plum']

# Создаём график ТОЛЬКО для rest
recording = 'rest'
# Фильтруем данные для rest
mask = df['Recording'] == recording
df_recording = df[mask]

# Собираем данные для barplot
means = []
stds = []
sems = []
labels = []

for headset in headsets:
    # Фильтруем данные для текущей гарнитуры
    mask_headset = df_recording['Headset'] == headset
    df_headset = df_recording[mask_headset]

    # Извлекаем данные по всем субъектам (Subject_1, Subject_2, ..., Subject_5)
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
        labels.append(headsets_mapping[headset])
    else:
        # Если после удаления NaN данных не осталось
        means.append(0)
        stds.append(0)
        sems.append(0)
        labels.append(headsets_mapping[headset])

# Создаём фигуру для rest
fig, ax = plt.subplots(figsize=(16, 12))

# Строим barplot с корректными параметрами для отображения «усов»
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

# Добавляем значения над столбцами
for bar, mean, sem in zip(bars, means, sems):
    if mean > 0:  # Не показываем 0
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

# Настройки графика
ax.set_title(recordings_mapping[recording], fontsize=24, pad=20)
ax.set_ylabel('Средняя доля загрязнённых эпох, %', fontsize=20)
ax.set_ylim(0, 100)
ax.tick_params(axis='y', labelsize=20)

# Устанавливаем подписи на оси X