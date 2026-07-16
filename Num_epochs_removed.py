import config as cfg
from functions import artifacts_share_into_df, plot_share_artifacts, read_artifacts

subjects = cfg.subjects
headsets_base = cfg.headsets_base
recordings_base = cfg.recordings_base
recordings_mapping = cfg.recordings_mapping
headsets_mapping = cfg.headsets_mapping

results = read_artifacts(subjects, headsets_base, recordings_base)
df = artifacts_share_into_df(results)
############################################# Plot #############################################################
plot_share_artifacts(df, aggtype='Recording', mapping=recordings_mapping, base=recordings_base)
plot_share_artifacts(df, aggtype='Headset',  mapping=headsets_mapping, base=headsets_base)