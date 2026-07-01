# Reproducible Runbook

## Environment

Tested with Python 3.12 on Windows. The smoke-test script uses relative paths only.

```bash
python -m pip install -r requirements.txt
```

## Smoke Test

```bash
python scripts/reproduce_results.py
```

## Expected Outputs

The command creates:

- `outputs/claim_checks.json`
- `outputs/claim_checks.csv`
- `outputs/figures/rebuilt_crosszonal_causation_burden.png`
- `outputs/figures/rebuilt_forecast_instability.png`

The smoke test verifies selected derived quantities and rebuilds diagnostic plots. It is intentionally fast and does not rerun every analysis script.

## Regenerate Publication Figures

The current figure scripts and derived inputs are in `code/`. From the repository root:

```bash
cd code
python fig_P0_mechanism.py
python fig_P2_placebo.py
python fig_P3_nonstationarity.py
python fig_P1_structural.py
python fig_P4_P5.py
```

Expected current figure outputs are written to `figures/`:

- `Figure_1.pdf/.svg/.png`
- `Figure_2.pdf/.svg/.png`
- `Figure_3.pdf/.svg/.png`
- `Figure_4.pdf/.svg/.png`
- `Figure_5.pdf/.svg/.png`
- `Supplementary_Figure_S2.pdf/.svg/.png`

`Supplementary_Figure_S1.pdf/.svg/.png` is an author-created static disclosure-chain schematic included in `figures/`; it has no quantitative dependency and is not rebuilt by the smoke test.

## Recompute Analysis Layers

These scripts rerun the public computational layer from the released derived inputs. Raw third-party source workbooks are not redistributed; scripts that require them document the expected local file boundary in code comments and in `DATASETS_AND_LINKS.csv`.

```bash
cd code
python amplification.py
python overprocurement.py
python expansion_analysis.py
python supply_elasticity.py
python miso_wedge.py
python structural_clearing.py
```

`structural_clearing.py` performs the largest Monte Carlo calculation and uses PyTorch. It runs on CPU when CUDA is unavailable, but runtime can be materially longer than the smoke test.

## Expected Checks

- Dominion 2026 causation share is about 61.6%.
- Dominion 2026 burden share is about 16.1%.
- Dominion causation/burden ratio is about 3.8.
- Comparable forecast-vintage revisions include +28% for the 2026 target and +65% for the 2027 target from the 2023 to 2025 vintage; the comparable 2023-2025 revision set is 5 up / 2 down and is not reported as a statistically significant ratchet.
- The repository contains no active manuscript PDF, cover letter, reviewer-response draft, internal `rounds/` or `logs/` directory.

## Non-Reproduced Items

Raw official workbooks and filings are not redistributed. Re-running the complete raw-data extraction from original official PDFs/XLSX files requires downloading the official records listed in `DATASETS_AND_LINKS.csv`, placing them under a local `data_raw/` directory, and following the locators in `tables/Supplementary_Table_3_data_source_inventory.csv`. The released package reproduces the public derived computational layer and key claim checks, not a redistribution of raw third-party source files.
