import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.formula.api import ols

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

# Создаём пример данных
np.random.seed(42)
n_subjects = 20
n_days = 5
n_obs = n_subjects * n_days

df = pd.DataFrame({
    'y': np.random.normal(0, 1, n_obs),
    'HeadsetType': np.random.choice(['ActiveNew', 'ActiveOld', 'PassiveNew', 'PassiveOld', 'Wet'], n_obs),
    'RecordingType': np.random.choice(['EyesOpen', 'EyesClosed', 'Bike'], n_obs),
    'Subject': np.repeat(range(n_subjects), n_days),
    'Day': np.tile(range(n_days), n_subjects)
})


# Создаём вложенную группирующую переменную
df['Subject_Day'] = df['Subject'].astype(str) + '_' + df['Day'].astype(str)

model = smf.mixedlm(
    "y ~ C(HeadsetType) + C(RecordingType)",
    data=df,
    groups=df['Subject'],           # внешний уровень — испытуемые
    re_formula='~1',             # случайный перехва́т для Subject
    vc_formula={'Day': '0 + C(Day)'}  # вложенный случайный перехва́т для Day
)

model_simple = smf.mixedlm(
    "y ~ C(HeadsetType) + C(RecordingType)",
    data=df,
    groups=df['Day'],
    re_formula='~1')

from statsmodels.formula.api import ols


model_ols = ols(
    "y ~ C(HeadsetType) + C(RecordingType)",
    data=df
).fit()
print(model_ols.summary())

result = model.fit()
#result = model_simple.fit()
print(result.summary())

# Boxplot по гарнитурам
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='HeadsetType', y='y')
plt.title('Распределение y по типам гарнитур')
plt.show()

# QQ-plot остатков
from scipy import stats
stats.probplot(model_ols.resid, dist="norm", plot=plt)
plt.title('QQ-plot остатков')
plt.show()