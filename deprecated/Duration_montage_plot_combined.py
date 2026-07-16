import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Путь к папке с данными
data_dir = r"C:\Users\msasha\Desktop\dry_electrodes\Эксперимент"

# Список файлов для загрузки (дни с 1 по 6)
experiment_files = [f"experiment_data_day_{day}.xlsx" for day in range(1, 7)]

# Переименования для типов гарнитур
order_mapping = {
    'ActiveNew': 'DRY active + MCScap-DrA1 + Brush Flex ',
    'ActiveOld': 'DRY active + MCScap-DrA1 + Brush Medium',
    'PassiveNew': 'DRY + MCScap-DrP1 + Brush Flex',
    'PassiveOld': 'DRY + MCScap-DrP1 + Brush Medium',
    'Wet': 'Мокрые'
}


# Порядок отображения гарнитур
order = ['ActiveNew', 'ActiveOld', 'PassiveNew', 'PassiveOld', 'Wet']
display_labels = [order_mapping[key] for key in order]

# Список для хранения DataFrames каждого дня
dataframes = []

# Загружаем и обрабатываем данные для каждого дня
for day in range(1, 7):
    file_path = os.path.join(data_dir, f"experiment_data_day_{day}.xlsx")

    try:
        # Загружаем данные из Excel
        df = pd.read_excel(file_path)
        # Переименовываем значения в HeadsetType
        #df['HeadsetType'] = df['HeadsetType'].map(headset_mapping).fillna(df['HeadsetType'])
        # Добавляем колонку с номером дня для отслеживания
        df['ExperimentDay'] = day

        # Сохраняем DataFrame в список
        dataframes.append(df)
        print(f"Данные за день {day} успешно загружены")

    except FileNotFoundError:
        print(f"Файл {file_path} не найден — пропускаем день {day}")
    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {e}")


# Объединяем все DataFrames в один
combined_df = pd.concat(dataframes, ignore_index=True)

# Группируем данные по типу гарнитуры
grouped_data = combined_df.groupby('HeadsetType')['Duration_of_montage'].apply(list)


print('grouped_data', grouped_data)
# Подготавливаем данные для графика (в нужном порядке)
data_for_plot = [grouped_data.get(ht, []) for ht in order]

# Создаём фигуру и график
fig, ax = plt.subplots(figsize=(14, 10))

# Строим barplot вместо boxplot
#colors = ['lightblue', 'lightgreen', 'lightcoral', 'gold', 'plum']
colors = ['lightblue', 'lightgreen', 'lightcoral', 'wheat', 'plum']
# Вычисляем средние значения и стандартные отклонения для каждой гарнитуры
means = [np.mean(data) if len(data) > 0 else 0 for data in data_for_plot]
stds = [np.std(data) if len(data) > 0 else 0 for data in data_for_plot]

n_samples = [len(data) for data in data_for_plot]
sems = [std / np.sqrt(n) if n > 0 else 0 for std, n in zip(stds, n_samples)]

# Создаём столбчатую диаграмму
bars = ax.bar(display_labels, means, yerr=sems, color=colors, edgecolor='navy', capsize=5, alpha=0.8)

# Настройки графика
#ax.set_title('Средняя длительность монтажа по типам гарнитур',
#             fontsize=16, fontweight='bold', pad=20)
#ax.set_xlabel('Тип гарнитуры', fontsize=16)
ax.set_ylabel('Средняя длит-ть монтажа, минуты', fontsize=20)

# Улучшаем внешний вид
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.tick_params(axis='both', which='major', labelsize=16)
ax.tick_params(axis='x', rotation=45)


# Добавляем значения над столбцами
for bar, mean in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
             f'{mean:.2f}', ha='center', va='bottom', fontsize=16, fontweight='bold')
"""
# Добавляем легенду с пояснением
legend_elements = [plt.Rectangle((0, 0), 1, 1, fc=color, edgecolor='navy', alpha=0.8)
                  for color in colors]

ax.legend(legend_elements, display_labels, title='Типы гарнитур',
          loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)
"""
# Сохраняем график
output_file = os.path.join(data_dir, 'средняя_длительность_монтажа_объединённые_данные.svg')
plt.tight_layout()
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print(f"График средней длительности монтажа сохранён в: {output_file}")


print(f"\nГрафик распределения длительности монтажа сохранён в: {output_file}")

# Выводим сводную статистику
print("\nСводная статистика по длительности монтажа (минуты):")
for headset_type in order:
    values = grouped_data.get(headset_type, [])
    if values:
        print(f"\n{headset_type}:")
        print(f"  Общее количество измерений: {len(values)}")
        print(f"  Среднее: {np.mean(values):.2f}")
        print(f"  Медиана: {np.median(values):.2f}")
        print(f"  Стандартное отклонение: {np.std(values):.2f}")
        print(f"  Минимум: {min(values):.2f}, Максимум: {max(values):.2f}")
    else:
        print(f"{headset_type}: нет данных")

# Дополнительно сохраняем объединённые данные в новый Excel-файл
output_excel = os.path.join(data_dir, 'объединённые_данные_эксперимента_дни_1_6.xlsx')
combined_df.to_excel(output_excel, index=False)
print(f"\nОбъединённые данные сохранены в Excel-файл: {output_excel}")
