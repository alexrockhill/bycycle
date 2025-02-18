"""Tests the main cycle-by-cycle feature computation function."""

import numpy as np

from bycycle.features import *

# Set data path
import os
import bycycle
DATA_PATH = '/'.join(os.path.dirname(bycycle.__file__).split('/')[:-1]) + '/tutorials/data/'

###################################################################################################
###################################################################################################

def test_compute_features():
    """Test cycle-by-cycle feature computation."""

    # Load signal
    sig = np.load(DATA_PATH + 'sim_stationary.npy')

    fs = 1000
    f_range = (6, 14)

    # Compute cycle features
    df = compute_features(sig, fs, f_range)

    # Check inverted signal gives appropriately opposite data
    df_opp = compute_features(-sig, fs, f_range, center_extrema='T')

    np.testing.assert_allclose(df['sample_peak'], df_opp['sample_trough'])
    np.testing.assert_allclose(df['sample_last_trough'], df_opp['sample_last_peak'])
    np.testing.assert_allclose(df['time_peak'], df_opp['time_trough'])
    np.testing.assert_allclose(df['time_rise'], df_opp['time_decay'])
    np.testing.assert_allclose(df['volt_rise'], df_opp['volt_decay'])
    np.testing.assert_allclose(df['volt_amp'], df_opp['volt_amp'])
    np.testing.assert_allclose(df['period'], df_opp['period'])
    np.testing.assert_allclose(df['time_rdsym'], 1 - df_opp['time_rdsym'])
    np.testing.assert_allclose(df['time_ptsym'], 1 - df_opp['time_ptsym'])
