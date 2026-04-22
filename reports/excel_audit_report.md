# Audit Report: K18to21charts.xlsx

## Overview
This report details the audit findings and corrections applied to the `K18to21charts.xlsx` file. The audit focused on identifying formula errors, broken references, and formatting inconsistencies across all sheets.

## Audit Findings

### 1. Formula Errors and Broken References
- **No critical formula errors** (such as `#REF!`, `#NAME?`, `#VALUE!`, `#DIV/0!`, `#N/A`) were detected in any of the visible or hidden sheets.
- **External Links:** No external workbook references were found. All data appears to be self-contained within the workbook.

### 2. Formatting Issues
- **Hidden Columns:** Several sheets contained hidden columns that could obscure data or analysis:
    - `21Analysis`: Column K was hidden.
    - `20Analysis`: Column K was hidden.
    - `19Analysis`: Column K was hidden.
    - `18Analysis`: Column K was hidden.
- **Merged Cells:** Extensive use of merged cells was noted in the following sheets:
    - `21Report`: Multiple ranges (e.g., B3:H3, D10:H10).
    - `19Data`: Header rows (A1:F2, G1:T1).
    - `19Report`: Header rows (A1:H3).
    - `18Data`: Range G1:L1.
    *Note: While merged cells are often used for presentation, they can interfere with data sorting and filtering. They were left intact to preserve the report's visual layout but are flagged for awareness.*
- **Hidden Sheets:** The sheet `_ChartData` was found to be hidden. This is common for background data used in charts and did not contain any errors.

## Fixes Applied

| Issue Type | Action Taken |
| :--- | :--- |
| **Hidden Columns** | All hidden columns in `21Analysis`, `20Analysis`, `19Analysis`, and `18Analysis` (specifically Column K) have been unhidden to ensure full visibility of the analysis. |
| **Hidden Rows** | A global check was performed, and any hidden rows were unhidden. |
| **Formula Validation** | All formulas were scanned; since no errors were found, no formula corrections were required. |

## Recommendations
- **Avoid Merged Cells:** For future data management, consider using "Center Across Selection" instead of merging cells to maintain compatibility with data tools.
- **Data Validation:** Ensure that any new data added to the `Data` sheets follows the existing structure to prevent future reference issues in the `Analysis` and `Report` sheets.

---
**Status:** The file has been audited and corrected for visibility issues. No functional formula errors were present.
