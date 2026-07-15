
import pandas as pd
import numpy as np

## Parameters of experiment
n_subjects = 1
subject_num = 6
day_num = 7
n_recordings = 3

# Garnitures
#headsets = ['ActiveNew', 'PassiveOld', 'Wet']
headsets = ['ActiveBrush', 'ActiveNanoTubes']

# Recording types
recordings_base = ['EyesOpen', 'EyesClosed', 'Bike']

# Create a data table
data = []
for subject in range(n_subjects):
    # Берём первый и последний элементы для перестановки
    first_last = [headsets[0], headsets[1]]
    # Перемешиваем их
    permuted = np.random.permutation(first_last).tolist()
    print(permuted)
    # Формируем итоговый порядок: перемешанный первый, затем 'Wet', затем перемешанный последний
    #subject_headsets = [permuted[0], 'Wet', permuted[1]]
    subject_headsets = [permuted[0], permuted[1]]

    # Для каждой гарнитуры в случайном порядке
    for headset in subject_headsets:
        # Случайный порядок типов записи для этой гарнитуры
        recording_order = np.random.permutation(recordings_base).tolist()

        # Для каждого типа записи в случайном порядке
        for recording in recording_order:
                data.append({
                    'HeadsetType': headset,
                    'RecordingType': recording,
                    'Subject': f'S{subject_num + subject:02d}',  # S01, S02, ...
                    'Day': day_num,
                    'Impedance': 0,
                    'Duration_of_montage': 0
                })

df = pd.DataFrame(data)

# Сохраняем в Excel
output_path = rf'C:\Users\msasha\Desktop\dry_electrodes\Эксперимент\experiment_data_day_{day_num}.xlsx'
df.to_excel(output_path, index=False)

# Выводим первые строки для проверки
print("First 10 lines of the data table:")
print(df.head(10))