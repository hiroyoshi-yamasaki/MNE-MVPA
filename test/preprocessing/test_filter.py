import os
from pathlib import Path
import tempfile
from unittest import TestCase

import mne

from mne_mvpa.preprocessing.filter import filter
from mne_mvpa.definitions import ROOT_DIR

SAMPLE_FILE = ROOT_DIR / "data" / "test_data" / "sample_raw.fif"


class TestFilter(TestCase):

    def test_filter(self):

        with tempfile.TemporaryDirectory() as tmp_dir:

            tmp_dir = Path(tmp_dir)

            # Test filter
            filter(raw_file=SAMPLE_FILE, out_file=tmp_dir / "outfile_raw.fif",
                   l_freq=0.1, h_freq=40.0, notch=50.0, raw_reader=mne.io.read_raw)

            filter(raw_file=SAMPLE_FILE, out_file=tmp_dir / "outfile2_raw.fif",
                   l_freq=0.1, h_freq=40.0, notch=[50.0, 100.0, 150.0], raw_reader=mne.io.read_raw)

            self.assertIn("outfile_raw.fif", os.listdir(tmp_dir))
            self.assertIn("outfile2_raw.fif", os.listdir(tmp_dir))
