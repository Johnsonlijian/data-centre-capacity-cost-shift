# Reproducible Runbook

## Environment

Tested with Python 3.12 on Windows. The smoke-test script uses relative paths only.

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python scripts/reproduce_results.py
```

## Expected Outputs

The command creates:

- `outputs/claim_checks.json`
- `outputs/claim_checks.csv`
- `outputs/figures/rebuilt_crosszonal_causation_burden.png`
- `outputs/figures/rebuilt_forecast_instability.png`

## Expected Checks

- Dominion 2026 causation share is about 61.6%.
- Dominion 2026 burden share is about 16.1%.
- Dominion causation/burden ratio is about 3.8.
- 2027 forecast-vintage revision from 2023 to 2025 is about +65%.
- The repository contains no active manuscript PDF, cover letter, reviewer-response draft, internal `rounds/` or `logs/` directory.

## Non-Reproduced Items

Raw official workbooks and filings are not redistributed. Re-running the complete raw-data extraction from original official PDFs/XLSX files requires downloading the official records listed in `DATASETS_AND_LINKS.csv` and following the locators in `tables/Table3_source_locking_checklist_R160.csv`.

