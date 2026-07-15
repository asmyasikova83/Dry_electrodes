
import os
import pandas as pd

# Испытуемые
испытуемые = ['Subject_01', 'Subject_02', 'Subject_03', 'Subject_04', 'Subject_05']

# Этапы оценки
этапы = ['При установке гарнитуры', 'После ношения гарнитуры в течение 20 минут']

# Типы гарнитур
гарнитуры = [
    'Мокрые: NeoRec cap 21 PROFESSIONAL',
    'Сухие: AnaRec cap 21 mini DRY active (новые)',
    'Сухие: AnaRec cap 21 mini DRY active (старые)',
    'NeoRec cap 21 mini DRY passive (новые)',
    'NeoRec cap 21 mini DRY passive (старые)'
]

# Создаём данные
data = []
for испытуемый in испытуемые:
    for этап in этапы:
        for гарнитура in гарнитуры:
            data.append({
                'Испытуемый': испытуемый,
                'Этап': этап,
                'Тип гарнитуры': гарнитура,
                'Рейтинг уровня комфорта (1–7)': ''
            })

# Создаём DataFrame
df = pd.DataFrame(data)

# Сохраняем в Excel
output_pics_dir = r"M:\DB Temp\physionet.org\files\dry_electrodes\epochs\tables"
output_file = 'рейтинг_уровня_комфорта.xlsx'
filepath = os.path.join(output_pics_dir, output_file)
df.to_excel(filepath , index=False)

print(f"Таблица сохранена в файл: {output_file}")