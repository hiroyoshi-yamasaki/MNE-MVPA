from pathlib import Path
from typing import Union

import mne
import numpy as np

from ..utils.logging import setup_logging

logger = setup_logging(name="coregistration", level="info", mne_level="info")


def get_trans(info_file: Union[str, Path], dst_dir: Path, subject: str, subjects_dir: Union[str, Path],
              fiducials: str = "auto",
              initial_n_iterations: int = 6, initial_nasion_weight: float = 2.0, distance: float = 5.0,
              final_n_iterations: int = 20, final_nasion_weight: float = 10.0):
    """
    Perform automated coregistration
    See https://mne.tools/stable/auto_tutorials/forward/25_automated_coreg.html
    :param info_file: path to FIF file
    :param dst_dir: path to directory to save trans file in
    :param subject: subject name
    :param subjects_dir: path to FreeSurfer `subjects_dir`
    :param fiducials: fiducials estimation, default 'auto'
    (see https://mne.tools/stable/generated/mne.coreg.Coregistration.html)
    :param initial_n_iterations: number of iterations for first ICP (see mne.coreg.Coregistration.html)
    :param initial_nasion_weight: nasion weight for first ICP (see mne.coreg.Coregistration.html)
    :param distance: max. distance to determine outliers (see mne.coreg.Coregistration.html)
    :param final_n_iterations: number of iterations for the final ICP (see mne.coreg.Coregistration.html)
    :param final_nasion_weight: nasion weight for the final ICP (see mne.coreg.Coregistration.html)
    :return:
    """

    # Setup
    info = mne.io.read_info(info_file)
    coreg = mne.coreg.Coregistration(info, subject=subject, subjects_dir=subjects_dir, fiducials=fiducials)

    # Initial fit
    coreg.fit_fiducials()

    # Refine with ICP
    coreg.fit_icp(n_iterations=initial_n_iterations, nasion_weight=initial_nasion_weight)

    # Omit bad points
    coreg.omit_head_shape_points(distance=distance / 1e3)  # millimeter to meter

    # Final ICP
    coreg.fit_icp(n_iterations=final_n_iterations, nasion_weight=final_nasion_weight)

    # Result summary
    dists = coreg.compute_dig_mri_distances() * 1e3  # in mm
    logger.info(f"Distance between HSP and MRI (mean/min/max): {np.mean(dists):.2f} mm "
                f"/ {np.min(dists):.2f} mm / {np.max(dists):.2f} mm")

    # Write result
    mne.write_trans(dst_dir / f"{subject}-auto-trans.fif", trans=coreg.trans, overwrite=True)
