from pathlib import Path
import json

import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt


def load_nifti_as_array(nifti_path):
    """Load a NIfTI file and return both the image object and NumPy array."""

    if not nifti_path.exists():
        raise FileNotFoundError(f"Missing NIfTI file: {nifti_path}")

    nifti_image = nib.load(nifti_path)
    image_array = nifti_image.get_fdata()

    return nifti_image, image_array


def load_label_map(label_map_path):
    """Load label map JSON and convert label keys from text to integers."""

    if not label_map_path.exists():
        raise FileNotFoundError(f"Missing label map file: {label_map_path}")

    label_map_text = label_map_path.read_text(encoding="utf-8")
    label_map_raw = json.loads(label_map_text)

    label_map = {}

    for label_value_as_text, label_name in label_map_raw.items():
        label_value = int(label_value_as_text)
        label_map[label_value] = label_name

    return label_map


def normalize_image_for_display(image_slice):
    """
    Normalize one 2D image slice for display.

    MRI intensity ranges can vary a lot.
    Percentile normalization makes the visualization easier to see.
    """

    low_value = np.percentile(image_slice, 1)
    high_value = np.percentile(image_slice, 99)

    clipped_slice = np.clip(image_slice, low_value, high_value)

    normalized_slice = (clipped_slice - low_value) / (high_value - low_value)

    return normalized_slice


def find_slice_with_largest_tumor(segmentation_array):
    """
    Find the z-slice with the largest number of tumor voxels.

    Background is label 0.
    Tumor labels are all non-zero labels.
    """

    tumor_mask = segmentation_array > 0

    tumor_voxels_per_slice = np.sum(tumor_mask, axis=(0, 1))

    best_slice_index = int(np.argmax(tumor_voxels_per_slice))

    if tumor_voxels_per_slice[best_slice_index] == 0:
        raise RuntimeError("No tumor voxels found in the segmentation mask.")

    return best_slice_index


def save_mri_modalities_figure(
    t1_array,
    t1gd_array,
    t2_array,
    flair_array,
    slice_index,
    output_path,
):
    """Save a 2 x 2 figure showing the four MRI sequences."""

    t1_slice = normalize_image_for_display(t1_array[:, :, slice_index])
    t1gd_slice = normalize_image_for_display(t1gd_array[:, :, slice_index])
    t2_slice = normalize_image_for_display(t2_array[:, :, slice_index])
    flair_slice = normalize_image_for_display(flair_array[:, :, slice_index])

    figure, axes = plt.subplots(2, 2, figsize=(8, 8))

    axes[0, 0].imshow(t1_slice.T, cmap="gray", origin="lower")
    axes[0, 0].set_title("T1")

    axes[0, 1].imshow(t1gd_slice.T, cmap="gray", origin="lower")
    axes[0, 1].set_title("T1gd / contrast-enhanced T1")

    axes[1, 0].imshow(t2_slice.T, cmap="gray", origin="lower")
    axes[1, 0].set_title("T2")

    axes[1, 1].imshow(flair_slice.T, cmap="gray", origin="lower")
    axes[1, 1].set_title("FLAIR")

    for axis in axes.ravel():
        axis.axis("off")

    figure.suptitle(f"MRI sequences at z-slice {slice_index}")
    figure.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=200)
    plt.close(figure)


def save_segmentation_figure(segmentation_array, slice_index, output_path):
    """Save a figure showing only the segmentation mask."""

    segmentation_slice = segmentation_array[:, :, slice_index]

    figure, axis = plt.subplots(figsize=(6, 6))

    axis.imshow(segmentation_slice.T, cmap="tab10", origin="lower", vmin=0, vmax=9)
    axis.set_title(f"Segmentation mask at z-slice {slice_index}")
    axis.axis("off")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=200)
    plt.close(figure)


def save_overlay_figure(
    base_image_array,
    segmentation_array,
    slice_index,
    title,
    output_path,
):
    """Save MRI slice with segmentation overlay."""

    base_slice = normalize_image_for_display(base_image_array[:, :, slice_index])
    segmentation_slice = segmentation_array[:, :, slice_index]

    tumor_overlay = np.ma.masked_where(segmentation_slice == 0, segmentation_slice)

    figure, axis = plt.subplots(figsize=(6, 6))

    axis.imshow(base_slice.T, cmap="gray", origin="lower")
    axis.imshow(
        tumor_overlay.T,
        cmap="tab10",
        origin="lower",
        alpha=0.45,
        vmin=0,
        vmax=9,
    )

    axis.set_title(title)
    axis.axis("off")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output_path, dpi=200)
    plt.close(figure)


def print_image_information(name, nifti_image, image_array):
    """Print shape, voxel spacing, and intensity range for one NIfTI image."""

    voxel_spacing = nifti_image.header.get_zooms()[:3]

    print(f"{name}")
    print(f"  shape: {image_array.shape}")
    print(f"  voxel spacing mm: {voxel_spacing}")
    print(f"  min value: {np.min(image_array):.3f}")
    print(f"  max value: {np.max(image_array):.3f}")
    print()


def print_segmentation_labels(segmentation_array, label_map):
    """Print labels found in the segmentation mask."""

    unique_labels = np.unique(segmentation_array).astype(int)

    print("Segmentation labels found:")
    print("-" * 80)

    for label_value in unique_labels:
        label_name = label_map.get(label_value, "unknown_label")
        voxel_count = int(np.sum(segmentation_array == label_value))
        print(f"  label {label_value}: {label_name}, voxels = {voxel_count}")

    print("-" * 80)
    print()


def main():
    project_root = Path(__file__).resolve().parents[1]

    case_id = "case_001"

    case_folder = (
        project_root
        / "data"
        / "raw"
        / "upenn_gbm_subset"
        / case_id
    )

    output_folder = project_root / "outputs"

    t1_path = case_folder / f"{case_id}_t1.nii.gz"
    t1gd_path = case_folder / f"{case_id}_t1gd.nii.gz"
    t2_path = case_folder / f"{case_id}_t2.nii.gz"
    flair_path = case_folder / f"{case_id}_flair.nii.gz"
    segmentation_path = case_folder / f"{case_id}_seg.nii.gz"
    label_map_path = case_folder / "label_map.json"

    label_map = load_label_map(label_map_path)

    t1_nifti, t1_array = load_nifti_as_array(t1_path)
    t1gd_nifti, t1gd_array = load_nifti_as_array(t1gd_path)
    t2_nifti, t2_array = load_nifti_as_array(t2_path)
    flair_nifti, flair_array = load_nifti_as_array(flair_path)
    segmentation_nifti, segmentation_array_float = load_nifti_as_array(segmentation_path)

    segmentation_array = segmentation_array_float.astype(np.uint8)

    print("=" * 80)
    print("Exploring real MRI case")
    print("=" * 80)
    print(f"Case folder: {case_folder}")
    print()

    print_image_information("T1 MRI", t1_nifti, t1_array)
    print_image_information("T1gd MRI", t1gd_nifti, t1gd_array)
    print_image_information("T2 MRI", t2_nifti, t2_array)
    print_image_information("FLAIR MRI", flair_nifti, flair_array)
    print_image_information("Segmentation mask", segmentation_nifti, segmentation_array)

    print_segmentation_labels(segmentation_array, label_map)

    best_slice_index = find_slice_with_largest_tumor(segmentation_array)

    print(f"Selected z-slice with largest tumor area: {best_slice_index}")
    print()

    save_mri_modalities_figure(
        t1_array=t1_array,
        t1gd_array=t1gd_array,
        t2_array=t2_array,
        flair_array=flair_array,
        slice_index=best_slice_index,
        output_path=output_folder / f"{case_id}_mri_modalities.png",
    )

    save_segmentation_figure(
        segmentation_array=segmentation_array,
        slice_index=best_slice_index,
        output_path=output_folder / f"{case_id}_segmentation.png",
    )

    save_overlay_figure(
        base_image_array=flair_array,
        segmentation_array=segmentation_array,
        slice_index=best_slice_index,
        title=f"FLAIR with segmentation overlay, z-slice {best_slice_index}",
        output_path=output_folder / f"{case_id}_flair_segmentation_overlay.png",
    )

    save_overlay_figure(
        base_image_array=t1gd_array,
        segmentation_array=segmentation_array,
        slice_index=best_slice_index,
        title=f"T1gd with segmentation overlay, z-slice {best_slice_index}",
        output_path=output_folder / f"{case_id}_t1gd_segmentation_overlay.png",
    )

    print("Saved figures:")
    print(f"  {output_folder / f'{case_id}_mri_modalities.png'}")
    print(f"  {output_folder / f'{case_id}_segmentation.png'}")
    print(f"  {output_folder / f'{case_id}_flair_segmentation_overlay.png'}")
    print(f"  {output_folder / f'{case_id}_t1gd_segmentation_overlay.png'}")
    print("=" * 80)


if __name__ == "__main__":
    main()