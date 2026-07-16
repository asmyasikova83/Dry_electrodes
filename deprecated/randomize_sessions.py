
import pandas as pd
import numpy as np

# Создаём пример данных
np.random.seed(42)

# Параметры эксперимента
n_subjects = 3  # число испытуемых
n_days = 5  # число дней (должно быть <= числа гарнитур)
n_recordings = 3  # число типов записи

# Гарнитуры (5 типов)
headsets = ['ActiveNew', 'ActiveOld', 'PassiveNew', 'PassiveOld', 'Wet']

# Типы записи (3 типа)
recordings_base = ['EyesOpen', 'EyesClosed', 'Bike']

# Создаём данные с правильной структурой
data = []
for subject in range(n_subjects):
    # Для каждого испытуемого — уникальный случайный порядок гарнитур
    subject_headsets = np.random.permutation(headsets).tolist()

    for day in range(n_days):
        # Берём гарнитуру по порядку (без возвращения)
        headset = subject_headsets[day]

        # Для этого дня — случайный порядок типов записи
        recording_order = np.random.permutation(recordings_base).tolist()

        for recording in recording_order:
            # Добавляем наблюдение
            data.append({
                'y': np.random.normal(0, 1),  # зависимая переменная
                'HeadsetType': headset,
                'RecordingType': recording,
                'Subject': f'S{subject:02d}',  # S01, S02, ...
                'Day': f'D{day:02d}'  # D01, D02, ...
            })

# Преобразуем в DataFrame
df = pd.DataFrame(data)

print(df[0:35])