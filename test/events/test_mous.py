import re
from unittest import TestCase

import numpy as np
import pandas as pd

from mne_mvpa.events.mous import combine_visual
from mne_mvpa.definitions import ROOT_DIR

MOUS_DIR = ROOT_DIR / "data" / "test_data" / "mous"


class MOUS(TestCase):

    def test_combine_events(self):

        events = np.load(MOUS_DIR / "visual_events.npy")
        original_df = pd.read_csv(MOUS_DIR / "sub-V1001_task-visual_events.tsv", sep="\t")

        events_df, error_df = combine_visual(events, original_df, tolerance=2)

        # Check data types
        self.assertEqual(events_df["sample"].dtype, np.int64, "sample dtype = int")
        self.assertEqual(events_df["onset"].dtype, np.float64, "onset dtype = float")
        self.assertEqual(events_df["duration"].dtype, np.float64, "duration dtype = float")
        self.assertTrue(pd.api.types.is_string_dtype(events_df["type"].dtype), "type dtype = str")
        self.assertTrue(pd.api.types.is_string_dtype(events_df["value"].dtype), "value dtype = str")
        self.assertEqual(events_df["sentence"].dtype, bool, "sentence dtype = bool")
        self.assertEqual(events_df["relative_clause"].dtype, bool, "relative_clause dtype = bool")
        self.assertEqual(events_df["target"].dtype, bool, "target dtype = bool")

        # Check for unusual values
        for _, row in events_df.iterrows():

            self.assertGreater(row["sample"], 0, "sample is positive")
            self.assertGreater(row["onset"], 0.0, "onset is positive")
            self.assertIn(row["type"], ["block", "fixation", "ISI", "pause", "question", "response", "word"])

            if row["type"] == "block":
                self.assertIn(row["value"], ["WOORDEN", "ZINNEN"], "only two kinds of mini-blocks")
            elif row["type"] == "fixation":
                self.assertEqual(row["value"], "NA", "fixation has no 'value'")
            elif row["type"] == "pause":
                self.assertEqual(row["value"], "NA", "pause has no 'value'")
            elif row["type"] == "response":
                self.assertIn(row["value"], ["1", "2", "3"], "response can be 1, 2, or 3")
            elif row["type"] == "word":
                self.assertIsNotNone(re.match(r"([\w.]+|<END>)", row["value"]), f"word is {row['value']}")
