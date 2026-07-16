import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Путь к папке с данными
output_pics_dir = r"M:\DB Temp\physionet.org\files\dry_electrodes\epochs\tables"
input_file = os.path.join(output_pics_dir, 'рейтинг_уровня_комфорта.xlsx')

# Загружаем данные
df = pd.read_excel(input_file)

# Фильтруем данные по этапам
montage = df[df['Этап'] == 'При установке гарнитуры']
after_20_min = df[df['Этап'] == 'После ношения гарнитуры в течение 20 минут']

print('montage ', montage)
print('after_20_min ', after_20_min)

# Определяем группы гарнитур
wet_garnetures = ['Мокрые']
dry_garnetures = [
    'DRY active + MCScap-DrA1 + Brush Flex',
    'DRY active + MCScap-DrA1 + Brush Medium',
    'DRY + MCScap-DrP1 + Brush Flex',
    'DRY + MCScap-DrP1 + Brush Medium'
]

# Функция для расчёта среднего рейтинга по группе гарнитур
def calculate_group_mean(data_frame, garneture_list):
    all_ratings = []
    for gar in garneture_list:
        ratings = data_frame[data_frame['Тип гарнитуры'] == gar]['Рейтинг уровня комфорта (1–7)'].dropna()
        all_ratings.extend(ratings.values)
    return np.mean(all_ratings) if all_ratings else 0, np.std(all_ratings) if all_ratings else 0

# Рассчитываем средние для мокрой и сухих групп на обоих этапах
mean_wet_mont, std_wet_mont = calculate_group_mean(montage, wet_garnetures)
mean_dry_mont, std_dry_mont = calculate_group_mean(montage, dry_garnetures)

mean_wet_after, std_wet_after = calculate_group_mean(after_20_min, wet_garnetures)
mean_dry_after, std_dry_after = calculate_group_mean(after_20_min, dry_garnetures)

# Подготавливаем данные для графиков
groups = ['Сухие системы', 'Мокрая система']
means_mont = [mean_dry_mont, mean_wet_mont]
std_mont = [std_dry_mont, std_wet_mont]

means_after = [mean_dry_after, mean_wet_after]
std_after = [std_dry_after, std_wet_after]

# Создаём фигуру с двумя подграфиками
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# График 1: При установке гарнитуры
x_positions = np.arange(len(groups))
width = 0.4

bars1 = ax1.bar(x_positions, means_mont, width, yerr=std_mont,
           color=['lightblue', 'lightcoral'], edgecolor=['navy', 'darkred'],
           capsize=5)

ax1.set_ylabel('Рейтинг комфорта (1–7)', fontsize=20)
ax1.set_title('Рейтинг комфорта при установке гарнитуры (1–7)', fontsize=20, fontweight='bold')
ax1.set_xticks(x_positions)
ax1.set_xticklabels(groups, fontsize=20)
ax1.grid(axis='y', alpha=0.3, linestyle='--')
ax1.legend()
# Увеличиваем шрифт меток на оси Y до 14 пт
ax1.tick_params(axis='y', labelsize=16)

# Добавляем значения над столбиками
for bar, mean in zip(bars1, means_mont):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
             f'{mean:.2f}', ha='center', va='bottom', fontsize=16, fontweight='bold')

# График 2: После 20 минут ношения
bars2 = ax2.bar(x_positions, means_after, width, yerr=std_after,
           color=['lightblue', 'lightcoral'], edgecolor=['navy', 'darkred'],
           capsize=5)

ax2.set_ylabel('Рейтинг комфорта (1–7)', fontsize=20)
ax2.set_title('Рейтинг комфорта после 20 минут ношения (1–7)', fontsize=20, fontweight='bold')
ax2.set_xticks(x_positions)
ax2.set_xticklabels(groups, fontsize=20)
ax2.grid(axis='y', alpha=0.3, linestyle='--')
ax2.legend()
ax2.tick_params(axis='y', labelsize=16)

# Добавляем значения над столбиками
for bar, mean in zip(bars2, means_after):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
             f'{mean:.2f}', ha='center', va='bottom', fontsize=16, fontweight='bold')

# Общие настройки
plt.tight_layout()

# Сохраняем график
output_file = os.path.join(output_pics_dir, 'сравнение_сухих_и_мокрой_систем_комфорт.svg')
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print(f"Графики сравнения сухих и мокрой систем сохранены в: {output_file}")

# Выводим статистику в консоль
print("\nСТАТИСТИКА ПО ГРУППАМ:")
print("При установке гарнитуры:")
print(f"Сухие системы: средний = {mean_dry_mont:.2f}, std = {std_dry_mont:.2f}")
print(f"Мокрая система: средний = {mean_wet_mont:.2f}, std = {std_wet_mont:.2f}")

print("\nПосле 20 минут ношения:")
print(f"Сухие системы: средний = {mean_dry_after:.2f}, std = {std_dry_after:.2f}")
print(f"Мокрая система: средний = {mean_wet_after:.2f}, std = {std_wet_after:.2f}")
