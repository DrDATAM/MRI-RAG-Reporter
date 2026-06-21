from pathlib import Path
import json

import requests


def download_file(source_url, output_path):
    """
    Download one file from source_url and save it to output_path.

    This function is intentionally simple:
    - if the file already exists, it skips downloading
    - if the download fails, it raises an error loudly
    """

    if output_path.exists():
        print(f"Already exists, skipping: {output_path}")
        return

    print(f"Downloading from:")
    print(f"  {source_url}")
    print(f"Saving to:")
    print(f"  {output_path}")

    response = requests.get(source_url, stream=True, timeout=120)

    if response.status_code != 200:
        raise RuntimeError(
            f"Download failed with status code {response.status_code}: {source_url}"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("wb") as output_file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                output_file.write(chunk)

    print("Download complete.")
    print()


def create_label_map(label_map_path):
    """
    Create a label map for the segmentation file.

    The segmentation mask is a 3D image where each voxel contains an integer label.

    For this UPENN-GBM tumor segmentation, we start with:
    0 = background
    1 = necrotic tissue / necrotic tumor core
    2 = peritumoral edema
    3 = enhancing tumor

    We will verify the actually present labels later in 01_inspect_segmentation.py.
    """

    label_map = {
        "0": "background",
        "1": "necrotic_tumor_core",
        "2": "peritumoral_edema",
        "3": "enhancing_tumor",
    }

    label_map_text = json.dumps(label_map, indent=4)
    label_map_path.write_text(label_map_text, encoding="utf-8")


def print_final_file_list(case_folder):
    print("=" * 80)
    print("Downloaded case files")
    print("=" * 80)

    for file_path in sorted(case_folder.iterdir()):
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"{file_path.name}: {file_size_mb:.2f} MB")

    print("=" * 80)


def main():
    project_root = Path(__file__).resolve().parents[1]

    # We use one real subject from the UPENN-GBM TCIA GitHub release.
    #
    # Original subject ID on GitHub:
    #   sub-002
    #
    # Project-local case ID:
    #   case_001
    #
    # This keeps the rest of the project simple and independent of the original name.
    subject_id = "sub-002"
    case_id = "case_001"

    # GitHub release where the UPENN-GBM files are stored.
    release_base_url = (
        "https://github.com/data-nih/tcia/releases/download/upenn-gbm"
    )

    # Local folder where this one subject will be saved.
    case_folder = (
        project_root
        / "data"
        / "raw"
        / "upenn_gbm_subset"
        / case_id
    )

    case_folder.mkdir(parents=True, exist_ok=True)

    # Each entry maps:
    #
    # original GitHub filename  ->  simple project filename
    #
    # We rename files so later scripts can use easy names:
    #   case_001_t1.nii.gz
    #   case_001_t1gd.nii.gz
    #   case_001_t2.nii.gz
    #   case_001_flair.nii.gz
    #   case_001_seg.nii.gz
    files_to_download = {
        # T1-weighted MRI volume.
        # This is an anatomical MRI image.
        f"{subject_id}_T1w.nii.gz": f"{case_id}_t1.nii.gz",

        # Contrast-enhanced T1-weighted MRI volume.
        # ce-gd means contrast-enhanced with gadolinium.
        # We rename this to t1gd because it is easier to read.
        f"{subject_id}_ce-gd_T1w.nii.gz": f"{case_id}_t1gd.nii.gz",

        # T2-weighted MRI volume.
        # This is another MRI contrast of the same brain.
        f"{subject_id}_T2w.nii.gz": f"{case_id}_t2.nii.gz",

        # FLAIR MRI volume.
        # FLAIR is often useful for edema or abnormal fluid-sensitive signal.
        f"{subject_id}_FLAIR.nii.gz": f"{case_id}_flair.nii.gz",

        # Tumor segmentation mask.
        # This is not an intensity image.
        # It contains integer labels for tumor subregions.
        f"{subject_id}_seg.nii.gz": f"{case_id}_seg.nii.gz",
    }

    print("=" * 80)
    print("Downloading one UPENN-GBM subject")
    print("=" * 80)
    print(f"Original subject ID: {subject_id}")
    print(f"Local case ID:       {case_id}")
    print(f"Output folder:       {case_folder}")
    print("=" * 80)
    print()

    for original_file_name, local_file_name in files_to_download.items():
        source_url = f"{release_base_url}/{original_file_name}"
        output_path = case_folder / local_file_name

        download_file(
            source_url=source_url,
            output_path=output_path,
        )

    # Create the label map next to the downloaded segmentation.
    label_map_path = case_folder / "label_map.json"
    create_label_map(label_map_path)

    print(f"Created label map: {label_map_path}")
    print()

    print_final_file_list(case_folder)


if __name__ == "__main__":
    main()