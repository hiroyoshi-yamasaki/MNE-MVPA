#!/bin/bash

# Script for performing FreeSurfer reconstruction of subject’s brain from nifti file
# Executing this will create SUBJECT/NAME with several folders (bem, label, mri etc.)
# See https://mne.tools/stable/auto_tutorials/forward/10_background_freesurfer.html
#
# NOTE: for MacOS, install gawk with `$ brew install gawk`
#
# Run the file as follows:
# `$ .../reconstruct.sh "path/to/freesurfer/home" "path/to/subjects/dir" "subject-name" "path/to/Nifti/file"`

HOME="$1"                         # path to FreeSurfer home
SUBJECTS="$2"                     # path to subjects_dir
NAME="$3"                         # name of the subject, e.g. 'sub-V1001'
NIFTI="$4"                        # path to Nifti file, e.g. .../sub-V1001/anat/sub-V1001_T1w.nii

export FREESURFER_HOME=$HOME
source "$FREESURFER_HOME/SetUpFreeSurfer.sh"
export SUBJECTS_DIR=$SUBJECTS

recon-all -i "$NIFTI" -s "$NAME" -all
