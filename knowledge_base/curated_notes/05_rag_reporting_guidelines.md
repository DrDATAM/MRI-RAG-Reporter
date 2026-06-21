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
