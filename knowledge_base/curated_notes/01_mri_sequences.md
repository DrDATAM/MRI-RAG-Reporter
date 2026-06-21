# MRI sequences used in this project

This project uses a real glioblastoma MRI case with multiple MRI sequences.

MRI is the broad imaging modality. Within MRI, different acquisition settings create different image contrasts. In brain tumor datasets, these different MRI sequences are often called modalities.

The four MRI sequences used in this project are:

- T1-weighted MRI
- contrast-enhanced T1-weighted MRI, also called T1-Gd or T1gd
- T2-weighted MRI
- FLAIR MRI

The segmentation mask is separate from these MRI images. The MRI files contain intensity values. The segmentation file contains integer labels for tumor regions.

## T1-weighted MRI

T1-weighted MRI is useful for anatomical structure.

Simple memory:

T1 = anatomy-focused image

In brain MRI, T1 provides structural reference. It helps locate anatomy and gives context for where the tumor is positioned.

## T1-Gd / contrast-enhanced T1

T1-Gd means T1-weighted MRI after gadolinium contrast.

Simple memory:

T1-Gd = enhancement image

Tumor regions with contrast enhancement may appear more visible on T1-Gd. Enhancing tumor labels are conceptually related to contrast-enhanced T1 images.

In the downloaded files, this appears as:

sub-002_ce-gd_T1w.nii.gz

In this project, it is renamed as:

case_001_t1gd.nii.gz

## T2-weighted MRI

T2-weighted MRI is sensitive to fluid-rich tissue.

Simple memory:

T2 = water/fluid-sensitive image

T2 can show edema, fluid-rich abnormality, necrotic/cystic regions, and tumor-associated signal changes. However, cerebrospinal fluid can also appear bright on T2.

## FLAIR MRI

FLAIR stands for Fluid-Attenuated Inversion Recovery.

Simple memory:

FLAIR = T2-like image where free fluid/CSF is suppressed

FLAIR is useful because edema and abnormal fluid-sensitive signal may remain visible, while free cerebrospinal fluid signal is reduced.

This helps peritumoral abnormality stand out more clearly in many brain tumor cases.

## Segmentation mask

The segmentation mask is not an MRI intensity image.

It is a label map.

Each voxel contains an integer label such as:

- 0 = background
- 1 = necrotic tumor core
- 2 = peritumoral edema
- 3 = enhancing tumor

The case summary in this project is computed from the segmentation mask.
