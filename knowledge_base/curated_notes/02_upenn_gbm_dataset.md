# UPENN-GBM dataset note

This project uses one subject from the UPENN-GBM data release hosted through TCIA/GitHub.

The downloaded subject is standardized locally as:

data/raw/upenn_gbm_subset/case_001/

The local files are:

- case_001_t1.nii.gz
- case_001_t1gd.nii.gz
- case_001_t2.nii.gz
- case_001_flair.nii.gz
- case_001_seg.nii.gz
- label_map.json

## What each file means

case_001_t1.nii.gz contains the T1-weighted MRI volume.

case_001_t1gd.nii.gz contains the contrast-enhanced T1-weighted MRI volume.

case_001_t2.nii.gz contains the T2-weighted MRI volume.

case_001_flair.nii.gz contains the FLAIR MRI volume.

case_001_seg.nii.gz contains the tumor segmentation mask.

label_map.json maps segmentation label values to readable tumor-region names.

## Why one case is enough for this project

This repository is not training a segmentation model.

The goal is to demonstrate a RAG pipeline over real segmented MRI data.

One real case is enough to show the complete workflow:

1. load real MRI data
2. load a real segmentation mask
3. extract quantitative tumor-region features
4. create a structured case summary
5. retrieve relevant domain knowledge
6. generate an educational report

More cases can be added later, but the first version stays intentionally small and laptop-friendly.
