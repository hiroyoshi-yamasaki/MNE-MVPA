import os
from pathlib import Path
from typing import Protocol

import mne

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent  # path to project root, MNE-MVPA


class RawReader(Protocol):
    def __call__(self, file: str, preload: bool) -> mne.io.Raw:
        pass
