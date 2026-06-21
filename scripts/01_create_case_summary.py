from pathlib import Path
import json

import nibabel as nib
import numpy as np


def load_label_map(label_map_path):
    """Load label map JSON and convert label keys from strings to integers."""

    if not label_map_path.exists():
        raise FileNotFoundError(f"Missing label map file: {label_map_path}")

    label_map_text = label_map_path.read_text(encoding="utf-8")
    label_map_raw = json.loads(label_map_text)

    label_map = {}

    for label_value_as_text, label_name in label_map_raw.items():
        label_value = int(label_value_as_text)
        label_map[label_value] = label_name

    return label_map


def calculate_voxel_volume_mm3(voxel_spacing_mm):
    """Calculate physical volume of one voxel in cubic millimeters."""

    voxel_volume_mm3 = (
        voxel_spacing_mm[0]
        * voxel_spacing_mm[1]
        * voxel_spacing_mm[2]
    )

    return voxel_volume_mm3


def create_label_statistics(segmentation_array, label_map, voxel_volume_mm3):
    """Calculate voxel count and physical volume for each label."""

    unique_labels = np.unique(segmentation_array).astype(int)

    label_statistics = {}

    for label_value in unique_labels:
        label_name = label_map.get(label_value, "unknown_label")

        voxel_count = int(np.sum(segmentation_array == label_value))
        volume_mm3 = voxel_count * voxel_volume_mm3
        volume_ml = volume_mm3 / 1000.0

        label_statistics[label_name] = {
            "label_value": int(label_value),
            "voxel_count": voxel_count,
            "volume_mm3": float(volume_mm3),
            "volume_ml": float(volume_ml),
        }

    return label_statistics


def calculate_region_group_summary(label_statistics, region_group_name, included_label_names):
    """
    Combine multiple labels into a larger anatomical/tumor region.

    Example:
    whole_tumor = necrotic_tumor_core + peritumoral_edema + enhancing_tumor
    tumor_core = necrotic_tumor_core + enhancing_tumor
    """

    total_voxel_count = 0
    total_volume_mm3 = 0.0
    total_volume_ml = 0.0

    for label_name in included_label_names:
        if label_name not in label_statistics:
            raise KeyError(
                f"Cannot calculate {region_group_name}. "
                f"Missing label in label_statistics: {label_name}"
            )

        total_voxel_count += label_statistics[label_name]["voxel_count"]
        total_volume_mm3 += label_statistics[label_name]["volume_mm3"]
        total_volume_ml += label_statistics[label_name]["volume_ml"]

    region_group_summary = {
        "included_regions": included_label_names,
        "voxel_count": int(total_voxel_count),
        "volume_mm3": float(total_volume_mm3),
        "volume_ml": float(total_volume_ml),
    }

    return region_group_summary


def create_case_summary(
    case_id,
    segmentation_path,
    label_map_path,
    output_summary_path,
):
    """Create a JSON summary from the segmentation mask."""

    if not segmentation_path.exists():
        raise FileNotFoundError(f"Missing segmentation file: {segmentation_path}")

    label_map = load_label_map(label_map_path)

    segmentation_nifti = nib.load(segmentation_path)
    segmentation_array_float = segmentation_nifti.get_fdata()
    segmentation_array = segmentation_array_float.astype(np.uint8)

    image_shape = segmentation_array.shape

    voxel_spacing_mm_raw = segmentation_nifti.header.get_zooms()[:3]
    voxel_spacing_mm = [float(value) for value in voxel_spacing_mm_raw]

    voxel_volume_mm3 = calculate_voxel_volume_mm3(voxel_spacing_mm)

    unique_labels = np.unique(segmentation_array).astype(int)
    unique_labels = [int(label_value) for label_value in unique_labels]

    label_statistics = create_label_statistics(
        segmentation_array=segmentation_array,
        label_map=label_map,
        voxel_volume_mm3=voxel_volume_mm3,
    )

    whole_tumor = calculate_region_group_summary(
        label_statistics=label_statistics,
        region_group_name="whole_tumor",
        included_label_names=[
            "necrotic_tumor_core",
            "peritumoral_edema",
            "enhancing_tumor",
        ],
    )

    tumor_core = calculate_region_group_summary(
        label_statistics=label_statistics,
        region_group_name="tumor_core",
        included_label_names=[
            "necrotic_tumor_core",
            "enhancing_tumor",
        ],
    )

    case_summary = {
        "case_id": case_id,
        "dataset": "UPENN-GBM subset from TCIA GitHub release",
        "source_segmentation_file": str(segmentation_path),
        "image_shape": [int(value) for value in image_shape],
        "voxel_spacing_mm": voxel_spacing_mm,
        "voxel_volume_mm3": float(voxel_volume_mm3),
        "unique_labels": unique_labels,
        "label_map": {
            str(label_value): label_name
            for label_value, label_name in label_map.items()
        },
        "label_statistics": label_statistics,
        "region_groups": {
            "whole_tumor": whole_tumor,
            "tumor_core": tumor_core,
        },
        "important_note": (
            "This summary is derived from a provided tumor segmentation mask. "
            "It is for educational RAG demonstration only and is not a clinical diagnosis."
        ),
    }

    output_summary_path.parent.mkdir(parents=True, exist_ok=True)

    output_summary_text = json.dumps(case_summary, indent=4)
    output_summary_path.write_text(output_summary_text, encoding="utf-8")

    return case_summary


def print_case_summary(case_summary, output_summary_path):
    """Print the most important parts of the case summary."""

    print("=" * 80)
    print("Case summary created")
    print("=" * 80)

    print(f"Case ID: {case_summary['case_id']}")
    print(f"Image shape: {case_summary['image_shape']}")
    print(f"Voxel spacing mm: {case_summary['voxel_spacing_mm']}")
    print(f"Voxel volume mm³: {case_summary['voxel_volume_mm3']:.3f}")
    print(f"Unique labels: {case_summary['unique_labels']}")

    print()
    print("Tumor-region volumes")
    print("-" * 80)
    print(f"{'Region':<32} | {'Voxels':>10} | {'Volume ml':>10}")
    print("-" * 80)

    for label_name, statistics in case_summary["label_statistics"].items():
        if label_name == "background":
            continue

        print(
            f"{label_name:<32} | "
            f"{statistics['voxel_count']:>10} | "
            f"{statistics['volume_ml']:>10.3f}"
        )

    print("-" * 80)

    whole_tumor = case_summary["region_groups"]["whole_tumor"]
    tumor_core = case_summary["region_groups"]["tumor_core"]

    print(
        f"{'whole_tumor':<32} | "
        f"{whole_tumor['voxel_count']:>10} | "
        f"{whole_tumor['volume_ml']:>10.3f}"
    )

    print(
        f"{'tumor_core':<32} | "
        f"{tumor_core['voxel_count']:>10} | "
        f"{tumor_core['volume_ml']:>10.3f}"
    )

    print()
    print(f"Saved summary to: {output_summary_path}")
    print("=" * 80)


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

    segmentation_path = case_folder / f"{case_id}_seg.nii.gz"
    label_map_path = case_folder / "label_map.json"

    output_summary_path = (
        project_root
        / "data"
        / "processed"
        / f"{case_id}_summary.json"
    )

    case_summary = create_case_summary(
        case_id=case_id,
        segmentation_path=segmentation_path,
        label_map_path=label_map_path,
        output_summary_path=output_summary_path,
    )

    print_case_summary(
        case_summary=case_summary,
        output_summary_path=output_summary_path,
    )


if __name__ == "__main__":
    main()