
data_dir = r'\\MCSSERVER\DB Temp\physionet.org\files\dry_electrodes\epochs'
output_pics_dir = r'\\MCSSERVER\DB Temp\physionet.org\files\dry_electrodes\epochs\pics'


# Rename headsets
headsets_mapping = {
    'active_new': 'DRY active + MCScap-DrA1 + Brush Flex ',
    'active_old': 'DRY active + MCScap-DrA1 + Brush Medium',
    'passive_new': 'DRY + MCScap-DrP1 + Brush Flex',
    'passive_old': 'DRY + MCScap-DrP1 + Brush Medium',
    'wet': 'Мокрые'
}

headsets_base = ['wet', 'active_new', 'active_old', 'passive_new', 'passive_old']
recordings_base = ['eyes_open', 'eyes_closed', 'cycling']

# Rename recordings
recordings_mapping = {
    'eyes_open': 'Покой: глаза открыты',
    'eyes_closed': 'Покой: глаза закрыты',
    'cycling': 'Движение'
    }
display_recordings = [recordings_mapping[key] for key in recordings_base]
subjects = ['S00', 'S01', 'S03', 'S04', 'S05']