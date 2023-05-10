from pathlib import Path
from typing import Union, List

import numpy as np

from ..definitions import RawReader


########################################################################################################################
# Filter the raw file                                                                                                  #
########################################################################################################################


def filter(raw_file: Union[str, Path], out_file: Union[str, Path],
           l_freq: float, h_freq: float, raw_reader: RawReader,
           filter_params: Union[None, dict] = None,
           notch: Union[None, List[float], float] = None, notch_max: float = 250.0,
           notch_params: Union[None, dict] = None):
    """
    A wrapper around `filter` and `notch_filter`
    :param raw_file: path to the raw file
    :param out_file: path to save the filtered file to
    :param l_freq: high-pass frequency
    :param h_freq: low-pass frequency
    :param raw_reader: dataset specific raw file reader, (path: str, preload: bool) -> mne.io.Raw
    :param filter_params: other parameters for filter function
    :param notch: either powerline frequency (float), list of notch frequencies (List[float]) or no notch filter (None)
        default is None
    :param notch_max: maximum frequency for notch filter, only used if powerline frequency is provided. e.g., if
        notch = 50.0, and notch_max = 250, then notch filter will be applied at 50, 100, 150, 200 Hz
    :param notch_params: other parameters for notch_filter function
    :return:
    """

    raw_file, out_file = str(raw_file), str(out_file)

    raw = raw_reader(raw_file, preload=True)

    # Filter
    if filter_params is None:
        filter_params = {}
    raw = raw.filter(l_freq, h_freq, **filter_params)

    # Notch filter
    if isinstance(notch, float):
        notch = np.arange(0, notch_max, notch)[1:]  # first is 0 Hz

    if notch is not None:
        if notch_params is None:
            notch_params = {}
        raw = raw.notch_filter(notch, **notch_params)

    raw.save(out_file)
