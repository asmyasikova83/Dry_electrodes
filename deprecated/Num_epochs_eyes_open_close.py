import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

dir = r'\\MCSSERVER\DB Temp\physionet.org\files\dry_electrodes\epochs'

# Переименования для типов гарнитур
headsets_mapping = {
    'active_new': 'DRY active + MCScap-DrA1 + Brush Flex ',
    'active_old': 'DRY active + MCScap-DrA1 + Brush Medium',
    'passive_new': 'DRY + MCScap-DrP1 + Brush Flex',
    'passive_old': 'DRY + MCScap-DrP1 + Brush Medium',
    'wet': 'Мокрые'
}

# Порядок отображения гарнитур
headsets = ['wet', 'active_new', 'active_old', 'passive_new', 'passive_old']
display_headsets = [headsets_mapping[key] for key in headsets]

"""
# Обновлённые записи: объединяем eyes_open и eyes_closed в 'rest'
recordings_base = ['rest', 'cycling']

# Переименования для типов записей
recordings_mapping = {
    'rest': 'Покой',
    'cycling': 'Движение'
}
"""
recordings_base = ['eyes_open', 'eyes_closed','cycling']

# Переименования для типов записей
recordings_mapping = {
    'eyes_open': 'Покой: глаза открыты',
    'eyes_closed': 'Покой: глаза закрыты',
    'cycling': 'Движение'
}

display_recordings = [recordings_mapping[key] for key in recordings_base]

subjects = ['S00', 'S01', 'S03', 'S04', 'S05']

# Функция для объединения данных eyes_open и eyes_closed в rest
def combine_rest_data(results):
    combined_results = {}
    for headset in results:
        combined_results[headset] = {}
        # Объединяем данные по eyes_open и eyes_closed
        rest_data = []
        for recording in ['eyes_open', 'eyes_closed']:
            if recording in results[headset]:
                rest_data.extend(results[headset][recording])
        # Удаляем NaN значения
        rest_data_clean = [x for x in rest_data if not np.isnan(x)]
        if rest_data_clean:
            combined_results[headset]['rest'] = rest_data_clean
        # Копируем данные по cycling
        if 'cycling' in results[headset]:
            combined_results[headset]['cycling'] = results[headset]['cycling']
    return combined_results


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



# Создаём DataFrame для Excel
data_for_excel = []

for headset in results:
    for recording in results[headset]:
        # Берём данные для этой комбинации headset/recording
        values = results[headset][recording]

        # Создаём строку для каждой комбинации
        row = {
            'Headset': headset,
            'Recording': recording,
            'Mean_Share_Artifacts': np.nanmean(values),
            'Std_Share_Artifacts': np.nanstd(values),
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



for recording in recordings_base:
    # Фильтруем данные для текущего recording
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

        # Удаляем NaN значения
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

    # Создаём фигуру для текущего recording
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
            'elinewidth': 3,
            'capsize': 10
        },
        linewidth=1
    )

    # Добавляем значения над столбцами
    for bar, mean, sem in zip(bars, means, sems):
        if mean > 0:  # Не показываем 0
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                mean,  # отступ от вершины уса
                f'{mean:.1f}%',
                ha='right',
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
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=20)

    # Сетка
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()

    # Сохраняем фигуру
    filename = f'artifacts_distribution_{recording}.svg'
    filepath = os.path.join(output_pics_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"График для '{recordings_mapping[recording]}' сохранён: {filepath}")