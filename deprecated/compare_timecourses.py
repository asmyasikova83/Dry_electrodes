import mne
import os
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

evoked_dir = r'\\MCSSERVER\DB Temp\physionet.org\files\dry_electrodes\evoked'
plots_dir = r'\\MCSSERVER\DB Temp\physionet.org\files\dry_electrodes'
os.makedirs(evoked_dir, exist_ok=True)

headsets = ['wet', 'active_new', 'active_old', 'passive_new', 'passive_old']

# Параметры для всех графиков
dpi = 300
figsize = (46, 8)

# Создаём одну фигуру с одной осью
fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

colors = plt.cm.tab10(np.linspace(0, 1, len(headsets)))  # палитра цветов

for i, headset in enumerate(headsets):
    # Формируем пути и имена
    filename = f'{headset}_eeg_10sec.fif'
    path_fif = os.path.join(evoked_dir, filename)
    print(path_fif)

    try:
        evokeds = mne.read_evokeds(path_fif)[0]  # читаем Evoked-файл
    except (OSError, FileNotFoundError):
        print(f'This file does not exist: {path_fif}')
        continue  # пропускаем, если файл не найден
    except Exception as e:
        print(f'Error reading {path_fif}: {e}')
        continue

    # Преобразуем данные в мкВ: из В (1e6) в мкВ (1e-6) → умножаем на 1e6
    evokeds_mean_uV = evokeds.get_data()[3] * 1e6  # мкВ T5 - T6
    #evokeds_mean_uV = np.mean(evokeds.get_data(), axis = 0)
    d =  evokeds.get_data()
    print('evokeds shape', d.shape)
    print('evokeds info', evokeds.info)
    print('evokeds_mean (мкВ)', evokeds_mean_uV.shape)
    # Определяем количество временных отсчётов
    n_times =  evokeds_mean_uV

    # Берём первую половину временных отсчётов для всех эпох и каналов
    half_data =  evokeds_mean_uV # форма: (n_epochs, n_channels, n_times//2)
    # Строим график
    ax.plot(
        half_data,
        label=f'{headset}',
        color=colors[i],
        linewidth=2.0,
        alpha=0.9
    )

# Настраиваем масштаб оси Y: от -10 до 10 мкВ
ax.set_ylim(-5, 5)

# Подписываем оси
ax.set_xlabel('Время (отсчёты)', fontsize=12)
ax.set_ylabel('Амплитуда (мкВ)', fontsize=12)

ax.set_title(
    'Сравнение временных рядов ЭЭГ: T5-T6, усреднение по всем испытуемым',
    fontsize=14,
    fontweight='bold'
)
#ax.set_ylim(-50, 50)
ax.grid(True, alpha=0.3, linestyle='--')

# Легенда — внутри графика, чтобы не перекрывать данные
ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, fontsize=10)

# Улучшаем расположение элементов
plt.tight_layout()

# Сохраняем фигуру
save_path = os.path.join(plots_dir, f'all_headsets_timecourses_averaged_10sec.png')
fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
print(f"График сохранён: {save_path}")

# Показываем фигуру
plt.show()
