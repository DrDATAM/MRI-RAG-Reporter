from pathlib import Path


def write_markdown_file(output_path, content):
    """
    Write one Markdown file.

    This is intentionally simple:
    - output_path tells us where the file goes
    - content is the Markdown text
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content.strip() + "\n", encoding="utf-8")


def main():
    project_root = Path(__file__).resolve().parents[1]

    knowledge_base_folder = (
        project_root
        / "knowledge_base"
        / "curated_notes"
    )

    markdown_files = {
        "01_mri_sequences.md": """
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
""",

        "02_upenn_gbm_dataset.md": """
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
""",

        "03_tumor_segmentation_labels.md": """
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
""",

        "04_measurements_from_segmentation.md": """
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
""",

        "05_rag_reporting_guidelines.md": """
# RAG reporting guidelines

The final report should combine two sources of information:

1. case_summary.json
2. retrieved knowledge-base context

The case summary provides case-specific measurements.

The knowledge base explains what the measurements and MRI terms mean.

## The report should include

A good educational report may include:

- case identifier
- available MRI sequences
- segmentation labels found
- volume of each tumor subregion
- whole tumor volume
- tumor core volume
- explanation of T1, T1-Gd, T2, and FLAIR
- explanation of segmentation-derived measurements
- limitations and safety note

## The report should avoid

The report should not claim:

- a clinical diagnosis
- tumor grade beyond what the dataset context already states
- prognosis
- treatment recommendation
- survival prediction
- radiologist-level interpretation
- uncertainty estimates that were not computed

## Grounding rule

Every numeric statement should come from case_summary.json.

Every explanatory statement should come from retrieved knowledge-base context.

If the retrieved context does not support a claim, the report should not make that claim.

## Suggested tone

The report should be written as an educational technical summary.

It should be understandable to a machine learning or medical imaging audience.

It should not sound like a clinical radiology report.
""",

        "06_limitations_and_safety.md": """
# Limitations and safety notes

This project is for educational and research demonstration purposes.

It is not a clinical diagnostic system.

## Segmentation-derived summary

The tumor measurements are derived from a pre-existing segmentation mask.

The repository does not train a segmentation model.

The repository does not verify whether the segmentation is clinically correct.

## MRI intensity limitations

MRI intensity values are not directly comparable across scanners, acquisition protocols, or preprocessing pipelines without careful normalization and quality control.

This first version focuses on segmentation-derived measurements rather than intensity-based biomarkers.

## Dataset limitations

The project uses one subject for the first demonstration.

One subject is enough to demonstrate the RAG pipeline, but it is not enough for population-level analysis.

## RAG limitations

RAG retrieves relevant text from a knowledge base, but retrieval can miss important context.

The LLM can still generate unsupported claims if the prompt is not restrictive.

For this reason, the report must be grounded in:

- case_summary.json for measurements
- retrieved knowledge-base text for explanations

## Clinical safety

The report should clearly state that it is not a diagnosis, not a treatment recommendation, and not a substitute for expert clinical review.
""",
    }

    print("=" * 80)
    print("Creating curated MRI knowledge base")
    print("=" * 80)

    for file_name, content in markdown_files.items():
        output_path = knowledge_base_folder / file_name

        write_markdown_file(
            output_path=output_path,
            content=content,
        )

        print(f"Created: {output_path}")

    print("=" * 80)
    print("Done.")
    print("=" * 80)


if __name__ == "__main__":
    main()