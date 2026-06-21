# Tumor segmentation labels

The segmentation mask stores integer labels.

In this project, the current label map is:

- 0 = background
- 1 = necrotic_tumor_core
- 2 = peritumoral_edema
- 3 = enhancing_tumor

The code should always read label_map.json instead of hard-coding label names in the report.

## Background

Background means voxels outside the labeled tumor regions.

Background is not included in tumor volume calculations.

## Necrotic tumor core

The necrotic tumor core label represents a tumor-core subregion associated with necrotic tissue.

In the project report, this should be described carefully as a segmentation-derived region, not as a new diagnosis.

## Peritumoral edema

The peritumoral edema label represents abnormal tissue around the tumor region, often associated with edema or infiltrative tumor-related signal change.

In many MRI workflows, FLAIR and T2 are important for understanding edema-like abnormality.

## Enhancing tumor

The enhancing tumor label represents tumor tissue that shows contrast enhancement.

This region is conceptually related to contrast-enhanced T1 imaging.

## Useful derived tumor groups

The project can calculate larger grouped regions from the segmentation labels.

Whole tumor:

necrotic_tumor_core + peritumoral_edema + enhancing_tumor

Tumor core:

necrotic_tumor_core + enhancing_tumor

These grouped measurements are derived from the segmentation mask and label map.
