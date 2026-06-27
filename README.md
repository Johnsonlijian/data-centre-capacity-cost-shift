# Data-Centre Capacity-Cost Shift

Reproducibility package for the manuscript:

**Committed before consumption: how forecast data-centre load socializes capacity cost**

This repository contains author-created code, derived tables and generated figures for reproducing the public-record computational layer of the manuscript. It does not contain the active submission manuscript, cover letter, reviewer-response drafts, internal rounds/logs or raw third-party official source files.

## What This Package Reproduces

- PJM cross-zonal causation-versus-burden shares from derived zone-level data.
- Forecast-vintage non-stationarity checks.
- Source-locking and variable-closure tables used to bound claims.
- Main manuscript figures and the supplementary closure-taxonomy figure.
- Reproducibility smoke tests that verify the key derived numerical claims in the package.

## Key Bounded Claims

- PJM three-auction above-embedded capacity-market effect: USD 21.26 billion, 45.0% of actual RPM revenue, from the Independent Market Monitor counterfactual.
- Dominion 2026 large-load adjustment share: about 61.6% of the PJM RTO adjustment, while its peak-load burden share is about 16%.
- The 2027 above-embedded adjustment rises from 8,300 MW in the 2023 forecast vintage to 13,668 MW in the 2025 vintage, a +65% revision.
- Household-dollar incidence is not point-identified from the public wholesale records; the package intentionally does not produce a household-bill estimate.

## Repository Structure

- `data/`: derived CSV datasets used by the reproducibility script.
- `tables/`: source-locking, closure, bridge and cross-market test tables.
- `figures/`: publication figures exported as PDF.
- `scripts/reproduce_results.py`: relative-path smoke test and diagnostic plot builder.
- `docs/public_private_boundary.md`: what is and is not released.
- `DATASETS_AND_LINKS.csv`: official source provenance and redistribution boundary.
- `REPRODUCIBLE_RUNBOOK.md`: commands to reproduce the checks.
- `CITATION.cff`: citation metadata for the public code/data package.

## Quick Start

```bash
python -m pip install -r requirements.txt
python scripts/reproduce_results.py
```

Expected outputs are written to `outputs/`, including `claim_checks.json`, `claim_checks.csv`, and regenerated diagnostic PNGs.

## License

Code is released under the MIT License. Author-created derived tables, documentation and generated figures are released under CC BY 4.0. Third-party official source materials are not redistributed and are not relicensed by this package.

