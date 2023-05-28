from pathlib import Path
from typing import Union
import mne


def get_forward_solution(info: mne.Info, trans: str, subject: str, subjects_dir: Union[str, Path], layers: int,
                         spacing: str = "ico5") -> mne.Forward:
    """
    Get forward model specific for the subject. https://mne.tools/stable/auto_tutorials/forward/30_forward.html
    :param info: Info object about the data
    :param trans: Transform for the measurement
    :param subject: subject name
    :param subjects_dir: path to freesurfer directory
    :param layers: whether to use 1 or 3 layers, use one layer to avoid problems. For MEG 1 is enough.
    :param spacing: spacing of dipoles
        Taken from https://mne.tools/stable/overview/cookbook.html#setting-up-source-space
         name     | Sources per hemisphere | Source spacing / mm  | Surface area per source / mm2 |
        'oct5'    |                   1026 |                 9.9  |                           97  |
        'ico4'    |                   2562 |                 6.2  |                           39  |
        'oct6'    |                   4098 |                 4.9  |                           24  |
        'ico5'    |                  10242 |                 3.1  |                           9.8 |
    :return:
        Forward model
    """

    src = mne.setup_source_space(subject, spacing=spacing, subjects_dir=subjects_dir)

    if layers == 3:
        conductivity = (0.3, 0.006, 0.3)    # for three layers
    elif layers == 1:
        conductivity = (0.3,)               # for single layer
    else:
        raise ValueError(f"Invalid layer number \"{layers}\" was given")

    model = mne.make_bem_model(subject=subject, ico=None, conductivity=conductivity, subjects_dir=subjects_dir)
    bem = mne.make_bem_solution(model)

    fwd = mne.make_forward_solution(info=info, trans=trans, src=src, bem=bem,
                                    meg=True, eeg=False, mindist=5.0, n_jobs=1)
    return fwd

