"""Tests burst detection."""

import itertools

import numpy as np

from neurodsp.filt import  filter_signal
from neurodsp.sim import sim_oscillation

from bycycle.features import compute_features

import pytest

from bycycle.burst import *

# Set data path
import os
import bycycle
DATA_PATH = '/'.join(os.path.dirname(bycycle.__file__).split('/')[:-1]) + '/tutorials/data/'

###################################################################################################
###################################################################################################

def test_detect_bursts_cycles():
    """Test amplitude and period consistency burst detection."""

    # Load signal
    sig = np.load(DATA_PATH + 'sim_bursting.npy')

    fs = 1000
    f_range = (6, 14)

    sig_filt = filter_signal(sig, fs, 'lowpass', 30, n_seconds=.3, remove_edges=False)

    # Compute cycle-by-cycle df without burst detection column
    df = compute_features(sig_filt, fs, f_range, burst_detection_method='amp',
                          burst_detection_kwargs={'amp_threshes': (1, 2),
                                                  'filter_kwargs': {'n_seconds': .5}})
    df.drop('is_burst', axis=1, inplace=True)

    # Apply consistency burst detection
    df_burst_cycles = detect_bursts_cycles(df, sig_filt)

    # Make sure that burst detection is only boolean
    assert df_burst_cycles.dtypes['is_burst'] == 'bool'
    assert df_burst_cycles['is_burst'].mean() > 0
    assert df_burst_cycles['is_burst'].mean() < 1
    assert np.min([sum(1 for _ in group) for key, group in \
        itertools.groupby(df_burst_cycles['is_burst']) if key]) >= 3


def test_detect_bursts_df_amp():
    """Test amplitude-threshold burst detection."""

    # Load signal
    sig = np.load(DATA_PATH + 'sim_bursting.npy')

    fs = 1000
    f_range = (6, 14)

    sig_filt = filter_signal(sig, fs, 'lowpass', 30, n_seconds=.3, remove_edges=False)

    # Compute cycle-by-cycle df without burst detection column
    df = compute_features(sig_filt, fs, f_range, burst_detection_method='amp',
                          burst_detection_kwargs={'amp_threshes': (1, 2),
                                                  'filter_kwargs': {'n_seconds': .5}})
    df.drop('is_burst', axis=1, inplace=True)

    # Apply consistency burst detection
    df_burst_amp = detect_bursts_df_amp(df, sig_filt, fs, f_range,
                                        amp_threshes=(.5, 1), n_cycles_min=4,
                                        filter_kwargs={'n_seconds': .5})

    # Make sure that burst detection is only boolean
    assert df_burst_amp.dtypes['is_burst'] == 'bool'
    assert df_burst_amp['is_burst'].mean() > 0
    assert df_burst_amp['is_burst'].mean() < 1
    assert np.min([sum(1 for _ in group) for key, group \
        in itertools.groupby(df_burst_amp['is_burst']) if key]) >= 4


@pytest.mark.parametrize("only_result", [True, False])
def test_plot_burst_detect_params(only_result):
    """Test plotting burst detection."""

    # Simulate oscillating time series
    n_seconds = 25
    fs = 1000
    freq = 10
    f_range = (6, 14)

    osc_kwargs = {'amplitude_fraction_threshold': 0,
                  'amplitude_consistency_threshold': .5,
                  'period_consistency_threshold': .5,
                  'monotonicity_threshold': .8,
                  'n_cycles_min': 3}

    sig = sim_oscillation(n_seconds, fs, freq)

    df = compute_features(sig, fs, f_range)

    fig = plot_burst_detect_params(sig, fs, df, osc_kwargs, plot_only_result=only_result)

    if not only_result:
        for param in fig:
            assert param is not None
    else:
        assert fig is not None
