import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.stats import friedmanchisquare
#from scikit_posthocs import posthoc_conover_friedman
import matplotlib.ticker as ticker

# Исходные данные
испытуемые = ['Subject_01', 'Subject_02', 'Subject_03', 'Subject_04', 'Subject_05']
гарнитуры = [
    'Мокрые',
    'DRY + MCScap-DrP1 + Brush Flex',
    'DRY + MCScap-DrP1 + Brush Medium'
]
этапы = ['Покой', 'Движение']  # предполагаем, что этапы есть

# Список колонок с импедансами
# Список колонок с импедансами
impedance_columns = ['Импеданс F3', 'Импеданс F4', 'Импеданс C3', 'Импеданс C4',
                    'Импеданс T5', 'Импеданс T6', 'Импеданс P3', 'Импеданс P4']

# Создаём пустой список для данных
data = []
# Сохраняем в Excel
dir = r"M:\DB Temp\physionet.org\files\dry_electrodes\epochs\tables"
filename = 'Импендансы.xlsx'

# Формируем полный путь к файлу
filepath = os.path.join(dir, filename)

# Читаем Excel‑файл
data = pd.read_excel(filepath)

# Преобразуем в DataFrame
df = pd.DataFrame(data)

# Фильтруем данные для каждой гарнитуры (только числовые колонки импеданса)
wet_data_filtered = df[df['Тип гарнитуры'] == 'Мокрые'][impedance_columns]
flex_data_filtered = df[df['Тип гарнитуры'] == 'DRY + MCScap-DrP1 + Brush Flex'][impedance_columns]
medium_data_filtered = df[df['Тип гарнитуры'] == 'DRY + MCScap-DrP1 + Brush Medium'][impedance_columns]

# Тест Фридмана — зависимые выборки
print("Выполняется тест Фридмана (зависимые выборки)")
# Выполняем тест Фридмана
stat, p_value = friedmanchisquare(
    wet_data_filtered.values.flatten(),
    flex_data_filtered.values.flatten(),
    medium_data_filtered.values.flatten()
)
print(stat, p_value )

print(df)

# Группируем по 'Тип гарнитуры' и рассчитываем среднее, игнорируя нули
mean_by_headset = df.groupby('Тип гарнитуры')[impedance_columns].mean().round(2)

# Рассчитываем SEM (стандартную ошибку среднего) для каждой гарнитуры
sem_by_headset = df.groupby('Тип гарнитуры')[impedance_columns].sem().mean(axis=1).round(0).astype(int)

# Способ 1: усреднить все значения в каждой строке (по гарнитуре)
average_impedance = mean_by_headset.mean(axis=1).round(0).astype(int)

# Преобразуем в датафрейм с одной колонкой, если нужно
result = pd.DataFrame({'Средний импеданс': average_impedance, 'SEM': sem_by_headset})


################################################################
# Визуализация
plt.figure(figsize=(12, 8))  # задаём размер графика

# Получаем список типов гарнитур (индексы датафрейма result)
headset_types = result.index.tolist()

# Получаем значения среднего импеданса и SEM
average_values = result['Средний импеданс'].tolist()
sem_values = result['SEM'].tolist()

# Задаём цвета
colors = ['lightcoral', 'wheat', 'plum']

# Строим столбчатую диаграмму с усами (SEM)
plt.bar(
    headset_types,
    average_values,
    yerr=sem_values,  # добавляем усы с SEM
    color=colors,
    edgecolor='black',
    alpha=0.7,
    capsize=10,      # размер «шапочек» на концах усов
    error_kw={
        'ecolor': 'black',      # цвет усов — красный для лучшей видимости
        'capsize': 10        # размер «шапочек» на концах
    }
)

# Добавляем подписи
ax = plt.gca()
ax.set_ylim(0, 1000000)  # ось Y: подберите под свои данные

# Настраиваем форматирование оси Y: преобразуем в формат «XK» (где X — тысячи)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda val, pos: f'{int(val // 1000)}K' if val >= 1000 else f'{val:.0f}'
))

plt.ylabel('Средний импеданс', fontsize=20)
# ВАЖНО: увеличиваем размер шрифта меток на оси Y
plt.tick_params(axis='y', labelsize=20)

# Вращаем подписи на оси X, если они длинные
plt.xticks(rotation=45, ha='right', fontsize=20)

# Добавляем значения над столбцами с учётом высоты уса
for i, (v, sem) in enumerate(zip(average_values, sem_values)):
    v_scaled = v // 1000  # целочисленное деление на 1000 — отбрасываем последние 3 цифры
    # Позиция текста: выше вершины уса
    plt.text(
        i,
        v ,  # отступ от вершины уса
        f'{v_scaled} кОм',
        ha='right',
        va='bottom',
        fontweight='bold',
        fontsize=16
    )

plt.tight_layout()


output_pics_dir = r"M:\DB Temp\physionet.org\files\dry_electrodes\epochs\tables"
output_file = os.path.join(output_pics_dir, 'Impedance.svg')
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()


