"""
3. Cycle-by-cycle analysis of resting state data
================================================

Say we ran an experiment and want to compare subjects' resting state data for some reason. Maybe we
want to study age, gender, disease state, or something. This has often been done to study
differences in oscillatory power or coupling between groups of people. In this notebook, we will run
through how to use bycycle to analyze resting state data.

In this example, we have 20 subjects (10 patients, 10 control), and we for some reason hypothesized
that their alpha oscillations may be systematically different. For example, (excessive hand waving)
we think the patient group should have more top-down input that increases the synchrony in the
oscillatory input (measured by its symmetry).

"""

####################################################################################################

import numpy as np
import scipy as sp
from scipy import stats
import matplotlib.pyplot as plt
from neurodsp.filt import filter_signal
from bycycle.features import compute_features
import pandas as pd
import seaborn as sns
pd.options.display.max_columns=50

####################################################################################################
#
# Load simulated experiment of 10 patients and 10 controls
# --------------------------------------------------------

####################################################################################################

# Load experimental data
sigs = np.load('data/sim_experiment.npy')
fs = 1000  # Sampling rate

# Apply lowpass filter to each signal
for idx in range(len(sigs)):
    sigs[idx] = filter_signal(sigs[idx], fs, 'lowpass', 30, n_seconds=.2, remove_edges=False)

####################################################################################################

# Plot an example signal
n_signals = len(sigs)
n_seconds = len(sigs[0])/fs
times = np.arange(0, n_seconds, 1/fs)

plt.figure(figsize=(16,3))
plt.plot(times, sigs[0], 'k')
plt.xlim((0, n_seconds))
plt.show()

####################################################################################################
#
# Compute cycle-by-cycle features
# -------------------------------

####################################################################################################

f_alpha = (7, 13) # Frequency band of interest
burst_kwargs = {'amplitude_fraction_threshold': .2,
                'amplitude_consistency_threshold': .5,
                'period_consistency_threshold': .5,
                'monotonicity_threshold': .8,
                'n_cycles_min': 3} # Tuned burst detection parameters

# Compute features for each signal and concatenate into single dataframe
dfs = []
for idx in range(n_signals):
    df = compute_features(sigs[idx], fs, f_alpha,
                          burst_detection_kwargs=burst_kwargs)
    if idx >= int(n_signals/2):
        df['group'] = 'patient'
    else:
        df['group'] = 'control'
    df['subject_id'] = idx
    dfs.append(df)
df_cycles = pd.concat(dfs)

####################################################################################################

print(df_cycles.head())

####################################################################################################
#
# Confirm appropriateness of burst detection parameters
# -----------------------------------------------------
#
# These burst detection parameters seem appropriate because they mostly restrict the analysis to
# periods of the signal that appear to be bursting. This was confirmed by looking at a few different
# signal segments from a few subjects.

subj = 1
sig_df = df_cycles[df_cycles['subject_id']==subj]
from bycycle.burst import plot_burst_detect_params
plot_burst_detect_params(sigs[subj], fs, sig_df,
                         burst_kwargs, tlims=(0, 5), figsize=(16, 3), plot_only_result=True)

plot_burst_detect_params(sigs[subj], fs, sig_df,
                         burst_kwargs, tlims=(0, 5), figsize=(16, 3))

####################################################################################################
#
# Analyze cycle-by-cycle features
# -------------------------------
#
# Note the significant difference between the treatment and control groups for rise-decay symmetry
# but not the other features

####################################################################################################

# Only consider cycles that were identified to be in bursting regimes
df_cycles_burst = df_cycles[df_cycles['is_burst']]

# Compute average features across subjects in a recording
features_keep = ['volt_amp', 'period', 'time_rdsym', 'time_ptsym']
df_subjects = df_cycles_burst.groupby(['group', 'subject_id']).mean()[features_keep].reset_index()
print(df_subjects)

####################################################################################################

feature_names = {'volt_amp': 'Amplitude',
                 'period': 'Period (ms)',
                 'time_rdsym': 'Rise-decay symmetry',
                 'time_ptsym': 'Peak-trough symmetry'}
for feat, feat_name in feature_names.items():
    graph = sns.catplot(x='group', y=feat, data=df_subjects)
    plt.xlabel('')
    plt.xticks(size=20)
    plt.ylabel(feat_name, size=20)
    plt.yticks(size=15)
    plt.tight_layout()
    plt.show()

####################################################################################################
#
# Statistical differences in cycle features
# -----------------------------------------

####################################################################################################

for feat, feat_name in feature_names.items():
    x_treatment = df_subjects[df_subjects['group']=='patient'][feat]
    x_control = df_subjects[df_subjects['group']=='control'][feat]
    ustat, pval = stats.mannwhitneyu(x_treatment, x_control)
    print('{:20s} difference between groups, U= {:3.0f}, p={:.5f}'.format(feat_name, ustat, pval))
