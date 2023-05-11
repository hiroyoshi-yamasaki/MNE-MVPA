import os
from pathlib import Path
import tempfile
from unittest import TestCase

import mne

from mne_mvpa.utils.logging import setup_logging, get_log_dir
from mne_mvpa.preprocessing.filter import filter
from mne_mvpa.definitions import ROOT_DIR

SAMPLE_FILE = ROOT_DIR / "data" / "test_data" / "sample_raw.fif"



class TestFilter(TestCase):

    def test_setup_logging(self):

        log_dir = get_log_dir()
        test_file = log_dir / "test.log"
        if test_file.exists():
            os.remove(test_file)

        logger = setup_logging(name="test", mne_level="info")

        with tempfile.TemporaryDirectory() as tmp_dir:

            logger.info("start testing")
            tmp_dir = Path(tmp_dir)

            filter(raw_file=SAMPLE_FILE, out_file=tmp_dir / "outfile_raw.fif",
                   l_freq=0.1, h_freq=40.0, notch=50.0, raw_reader=mne.io.read_raw)

            logger.warning("end testing")

            self.assertTrue(test_file.exists(), "log file exists")

            with open(test_file, "r") as f:
                file = f.read()

            self.assertRegex(file, r".*start testing.*", "info")
            self.assertRegex(file, r".*end testing.*", "warn")
