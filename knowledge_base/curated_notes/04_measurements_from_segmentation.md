# Measurements from segmentation

The project extracts quantitative measurements from the segmentation mask.

These measurements are not produced by a neural network in this repository. They are computed from the existing segmentation labels.

## Voxel count

Voxel count is the number of voxels belonging to a label.

Example:

If 5000 voxels have label 2, then the voxel count for peritumoral edema is 5000.

## Voxel spacing

Voxel spacing tells us the physical size of one voxel in millimeters.

Example:

voxel spacing = [1.0, 1.0, 1.0] mm

means one voxel is 1 mm by 1 mm by 1 mm.

## Voxel volume

Voxel volume is calculated as:

voxel_volume_mm3 = spacing_x * spacing_y * spacing_z

If voxel spacing is [1.0, 1.0, 1.0] mm, then:

voxel_volume_mm3 = 1.0 mm³

## Region volume

Region volume is calculated as:

region_volume_mm3 = voxel_count * voxel_volume_mm3

The project also reports volume in milliliters:

region_volume_ml = region_volume_mm3 / 1000

## Whole tumor volume

Whole tumor volume combines all tumor labels:

necrotic_tumor_core + peritumoral_edema + enhancing_tumor

This is a useful summary of total segmented tumor-related burden.

## Tumor core volume

Tumor core volume combines:

necrotic_tumor_core + enhancing_tumor

This excludes the edema label.

## Volume ratios

Useful ratios can be added later, for example:

enhancing_tumor_volume / whole_tumor_volume

edema_volume / whole_tumor_volume

tumor_core_volume / whole_tumor_volume

These ratios should be interpreted as segmentation-derived descriptive features, not clinical conclusions.
