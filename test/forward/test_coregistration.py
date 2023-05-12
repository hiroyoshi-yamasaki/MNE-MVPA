import os
from pathlib import Path
import tempfile
from unittest import TestCase

import mne

from mne_mvpa.forward.coregistration import get_trans
from mne_mvpa.definitions import ROOT_DIR

SAMPLE_FILE = ROOT_DIR / "data" / "test_data" / "sample_raw.fif"


class TestCoregistration(TestCase):

    def test_get_trans(self):

        with tempfile.TemporaryDirectory() as tmp_dir:

            tmp_dir = Path(tmp_dir)
            data_path = mne.datasets.sample.data_path()
            subjects_dir = data_path / "subjects"
            subject = "sample"

            # Test filter
            get_trans(info_file=SAMPLE_FILE, dst_dir=tmp_dir, subject=subject,
                      subjects_dir=subjects_dir)

            self.assertIn(f"{subject}-auto-trans.fif", os.listdir(tmp_dir))
