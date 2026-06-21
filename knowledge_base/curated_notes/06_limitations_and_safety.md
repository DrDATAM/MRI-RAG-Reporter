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
