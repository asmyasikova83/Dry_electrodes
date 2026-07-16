import os
import pandas as pd
import matplotlib.pyplot as plt

# Путь для сохранения графиков
output_pics_dir = r"M:\DB Temp\physionet.org\files\dry_electrodes\epochs\tables"
os.makedirs(output_pics_dir, exist_ok=True)

# Загружаем данные из Excel
input_file = os.path.join(output_pics_dir, 'анкета_результаты.xlsx')
df = pd.read_excel(input_file, sheet_name='Результаты_анкетирования')

# Удаляем столбец «Испытуемый» — он не нужен для анализа ответов
questions_df = df.drop('Испытуемый', axis=1)



# Цвета для графиков
colors = ['lightcoral', 'lightblue', 'lightgreen', 'gold', 'plum', 'skyblue']


# Строим отдельные графики для каждого вопроса
for idx, column in enumerate(questions_df.columns):
    # Считаем частоту каждого ответа
    value_counts = questions_df[column].value_counts()
    labels = value_counts.index.tolist()
    values = value_counts.values.tolist()

    # Выбираем цвет (циклически)
    color = colors[idx % len(colors)]

    # Определяем ширину столбиков: тонкие для одного ответа, стандартные для нескольких
    if len(labels) == 1:
        bar_width = 0.3  # тонкий столбик для одного ответа
    else:
        bar_width = 0.6  # стандартная ширина для нескольких ответов

    x_pos = range(len(labels))

    # Создаём отдельный график для каждого вопроса
    plt.figure(figsize=(10, 6))
    plt.bar(x_pos, values, width=bar_width, color=color,
             edgecolor='darkslategrey', linewidth=1, alpha=0.8)

    # Подписи значений над столбиками
    for x, v in zip(x_pos, values):
        plt.text(x, v + 0.05, str(v), ha='center', va='bottom',
                 fontsize=14, fontweight='bold')

    # Настройки графика
    plt.title(column, fontsize=16, fontweight='bold', pad=15)
    plt.ylabel('Количество ответов', fontsize=16)
    plt.xlabel('Варианты ответов', fontsize=16)
    plt.xticks(x_pos, labels, rotation=45, ha='right', fontsize=14)
    plt.yticks(fontsize=14)
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.gca().set_axisbelow(True)  # сетка под графиками

    # Формируем имя файла: очищаем название вопроса от спецсимволов
    safe_column_name = ''.join(c for c in column if c.isalnum() or c in ' _-').strip()[:50]
    filename = f'distribution_{safe_column_name}.png'
    filepath = os.path.join(output_pics_dir, filename)

    # Сохраняем отдельный график
    plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"График сохранён: {filepath}")

print(f"\nВсе графики распределения ответов сохранены в директории: {output_pics_dir}")
print(f"Всего создано графиков: {len(questions_df.columns)}")