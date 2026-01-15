# Clinical Variant Interpretation Pipeline (GRCh38)

## Background
Clinical interpretation of genomic variants requires combining raw variant calls
with curated knowledge bases and transparent prioritization rules.
This repository demonstrates a simplified but realistic clinical-style workflow
for variant interpretation using publicly available data.

The goal is to show how bioinformatics supports clinical and translational research
in a reproducible and auditable manner.

## Input / Output
**Input:** VCF aligned to GRCh38  
**Output:** annotated TSV, prioritized CSV, HTML report

## Workflow Overview
1. Parse VCF
2. Annotate with ClinVar (VCF-based)
3. Prioritize variants (clinical significance first)
4. Generate an HTML report

## Repository Structure
```text
clinical-variant-pipeline-grch38/
├── src/
├── example_data/
├── results/
├── docs/
├── requirements.txt
└── README.md

## Disclaimer
This project is intended for **research and educational purposes only**.
It is **not** a certified clinical pipeline and must **not** be used for
clinical diagnosis, treatment decisions, or patient care.

## ClinVar Annotation (GRCh38)

This pipeline annotates variants with ClinVar using the official NCBI VCF
(tabix-indexed, GRCh38).

For demonstration purposes, example variants may not be present in ClinVar,
resulting in empty ClinVar fields. This is expected behavior and documented
to ensure transparency of the workflow.

ClinVar fields added:
- CLNSIG (clinical significance)
- CLNDN (disease name)
- ALLELEID (ClinVar allele ID)
