import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.stats import friedmanchisquare, kruskal
from scikit_posthocs import posthoc_conover_friedman, posthoc_dunn
import matplotlib.pyplot as plt
import seaborn as sns

# Путь к папке с данными
data_dir = r"C:\Users\msasha\Desktop\dry_electrodes\Эксперимент"

# Список файлов для загрузки (дни с 1 по 6)
experiment_files = [f"experiment_data_day_{day}.xlsx" for day in range(1, 7)]

# Переименования для типов гарнитур
order_mapping = {
    'active_new': 'DRY active + MCScap-DrA1 + Brush Flex ',
    'active_old': 'DRY active + MCScap-DrA1 + Brush Medium',
    'passive_new': 'DRY + MCScap-DrP1 + Brush Flex',
    'passive_old': 'DRY + MCScap-DrP1 + Brush Medium',
    'wet': 'Мокрые'
}


# Группировка по категориям
'''
categories = {
    'New': ['ActiveNew', 'PassiveNew'],
    'Old': ['ActiveOld', 'PassiveOld'],
    'Wet': ['Wet']
}
category_labels = ['Сухие + Brush Flex', 'Сухие + Brush Medium', 'Мокрые']
category_colors = ['lightblue', 'lightgreen', 'lightcoral']

'''
categories = {
    'Active': ['ActiveNew', 'ActiveOld'],
    'Passive': ['PassiveNew', 'PassiveOld'],
    'Wet': ['Wet']
}
category_labels = ['Сухие Активные', 'Сухие Пассивные', 'Мокрые']
category_colors = ['plum', 'lightgray', 'lightcoral']

# Список для хранения DataFrames каждого дня
dataframes = []

# Загружаем и обрабатываем данные для каждого дня
for day in range(1, 7):
    file_path = os.path.join(data_dir, f"experiment_data_day_{day}.xlsx")

    try:
        # Загружаем данные из Excel
        df = pd.read_excel(file_path)
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

# Агрегируем данные по категориям
category_data = {}
for category, headsets in categories.items():
    # Фильтруем данные для текущей категории
    category_df = combined_df[combined_df['HeadsetType'].isin(headsets)]
    # Собираем все длительности монтажа в один список
    durations = category_df['Duration_of_montage'].dropna().tolist()
    category_data[category] = durations

print('category_data', category_data)

# Вычисляем средние значения и стандартные отклонения для каждой категории
means = []
stds = []
n_samples = []
sems = []
"""
# Подготовка данных для статистического теста
# Создаём словарь с данными по категориям
category_data = {}
for category, headsets in categories.items():
    category_df = combined_df[combined_df['HeadsetType'].isin(headsets)]
    # Если есть группировка по испытуемым/сессиям, используем pivot
    if 'Subject' in combined_df.columns:
        # Для теста Фридмана нужны данные в формате: строки — испытуемые, столбцы — условия
        pivot_data = category_df.pivot_table(
            values='Duration_of_montage',
            index='Subject',
            columns='HeadsetType',
            aggfunc='mean'
        )
        # Объединяем данные по типам внутри категории
        print('pivot_data',pivot_data)
        category_values = pivot_data.mean(axis=1)  # среднее по HeadsetType для каждого испытуемого
    else:
        # Просто объединяем все значения внутри категории
        category_values = category_df['Duration_of_montage'].dropna().values
    category_data[category] = category_values

print('category_data', category_data)
"""
# Извлекаем данные для теста
'''
new_data = category_data['New']
old_data = category_data['Old']
'''
active_data = category_data['Active']
passive_data = category_data['Passive']

wet_data = category_data['Wet']
'''
# Определяем, какой тест использовать
if 'Subject' in combined_df.columns and len(combined_df['Subject'].unique()) > 1:
    # Тест Фридмана — зависимые выборки
    print("Выполняется тест Фридмана (зависимые выборки)")
    #stat, p_value = friedmanchisquare(new_data, old_data, wet_data)
    stat, p_value = friedmanchisquare(active_data, passive_data, wet_data)
    test_name = "тест Фридмана"

print(f"\nРезультаты {test_name} теста:")
print(f"Статистика: {stat:.4f}")
print(f"p‑значение: {p_value:.4f}")

# Интерпретация результата
alpha = 0.05
if p_value < alpha:
    print(f"p < {alpha} — есть статистически значимые различия между категориями")

    # Пост‑хок анализ
    print("\nВыполняется пост‑хок анализ...")

    # Создаём DataFrame для post‑hoc тестов
    data_list = []
    for category in ['New', 'Old', 'Wet']:
        for value in category_data[category]:
            data_list.append({'Category': category, 'Duration': value})
    posthoc_df = pd.DataFrame(data_list)

    # Для Фридмана используем Conover test
    posthoc = posthoc_conover_friedman(posthoc_df, val_col='Duration', group_col='Category')

    print("\nРезультаты пост‑хок анализа (скорректированные p‑значения):")
    print(posthoc)
else:
    print(f"p ≥ {alpha} — нет статистически значимых различий между категориями")
'''
# Визуализация с указанием значимости
fig, ax = plt.subplots(figsize=(10, 8))
'''
means = [np.mean(category_data[cat]) for cat in ['New', 'Old', 'Wet']]
stds = [np.std(category_data[cat]) for cat in ['New', 'Old', 'Wet']]
n_samples = [len(category_data[cat]) for cat in ['New', 'Old', 'Wet']]
'''

means = [np.mean(category_data[cat]) for cat in ['Active', 'Passive', 'Wet']]
stds = [np.std(category_data[cat]) for cat in ['Active', 'Passive', 'Wet']]
n_samples = [len(category_data[cat]) for cat in ['Active', 'Passive', 'Wet']]

sems = [std / np.sqrt(n) if n > 0 else 0 for std, n in zip(stds, n_samples)]

# Создаём фигуру и график
fig, ax = plt.subplots(figsize=(10, 8))

bars = ax.bar(
    category_labels,
    means,
    yerr=sems,
    color=category_colors,
    edgecolor='navy',
    capsize=5,
    alpha=0.8,
    linewidth=1
)

# Добавляем значения над столбцами
for bar, mean, sem in zip(bars, means, sems):
    if mean > 0:  # Не показываем подписи для нулевых значений
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # Горизонтальная позиция — по центру столбца
            mean ,  # Вертикальная позиция — над столбцом с небольшим отступом (учитывает планку ошибки)
            f'{mean:.1f}',  # Текст: значение с одним знаком после запятой и символом %
            ha='center',  # Выравнивание по горизонтали: по центру
            va='bottom',  # Выравнивание по вертикали: снизу (текст растёт вверх)
            fontsize=16,  # Размер шрифта
            fontweight='bold',  # Жирное начертание
            color='darkblue'  # Цвет текста
        )
'''
# Добавляем значимость на график
if p_value < alpha:
    ax.text(0.5, max(means) * 1.1, '*', ha='center', va='bottom', fontsize=20, fontweight='bold')
'''
#ax.set_title(f'Средняя длительность монтажа по категориям гарнитур\n({test_name}: p = {p_value:.3f})',
#             fontsize=16, fontweight='bold', pad=20)
#ax.set_xlabel('Тип сенсоров', fontsize=14)
ax.set_ylabel('Средняя длит-ть монтажа, мин', fontsize=20)

ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.tick_params(axis='both', which='major', labelsize=18)
#ax.set_xticklabels(ordered_df.index, rotation=45, ha='right', fontsize=20)

# Разворачиваем подписи на оси X на 45 градусов
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
plt.tight_layout()

# СОХРАНЯЕМ ГРАФИК ДО ЗАКРЫТИЯ
#output_file = os.path.join(data_dir, 'средняя_длительность_монтажа_Flex_vs_Medium.svg')
output_file = os.path.join(data_dir, 'средняя_длительность_монтажа_Active_vs_Passive.svg')
plt.savefig(output_file, dpi=300, bbox_inches='tight')

# Вывод подробной статистики
print("\nПодробная статистика по категориям:")
for i, category in enumerate(['New', 'Old', 'Wet']):
    print(f"{category_labels[i]}: среднее = {means[i]:.2f} мин, "
          f"SD = {stds[i]:.2f}, n = {n_samples[i]}")