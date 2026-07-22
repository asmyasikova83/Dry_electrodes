from functions import randomize_sessions

## Parameters of experiment
n_subjects = 1
subject_num = 6
day_num = 7

# Garnitures
#headsets = ['ActiveNew', 'PassiveOld', 'Wet']
headsets = ['ActiveBrush', 'ActiveNanoTubes']

# Recording types
recordings_base = ['EyesOpen', 'EyesClosed', 'Bike']

df = randomize_sessions(n_subjects, subject_num, day_num, headsets, recordings_base)

print("First 10 lines of the data table:")
print(df.head(10))