# Customer segmentation web app

An educational RFM customer segmentation app with a Persian Streamlit interface, interactive charts, CSV upload, customer search, and downloadable results. Python and NumPy implement K-means directly so the clustering steps remain easy to study.

## Quick start (Windows)

Tested with Python 3.11. Run from this project directory:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

Open the local URL printed in the terminal, normally http://localhost:8501. Stop with Ctrl+C. You can also double-click **Start App.cmd** after setup. If the port is occupied:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 --server.port=8502
```

The original installation is at `E:\Machine-Learning\customer-segmentation`. Code, project packages, installer cache, and temporary setup files are stored there. The virtual environment still uses the existing base Python interpreter. No public deployment or account is needed.

## Try the interface

1. Keep **دادهٔ نمونه** selected to explore 400 synthetic customers.
2. Choose 2–8 groups and click **اجرای تحلیل**.
3. Inspect the customer map and the segment summary.
4. Switch to **فهرست مشتریان** to filter groups and search customer IDs.
5. Switch to **روش و کیفیت** to inspect the silhouette score and methodology.
6. Download customer assignments, group summaries, or a JSON audit report.
7. Select **بارگذاری CSV** to analyze your own order data.

The bundled `sample_orders.csv` is synthetic, reproducible with `generate_demo.py`, and does not represent real business results. It needs no internet connection. The local app processes uploads in memory and does not automatically save them to disk. Streamlit caches analysis results in process memory for up to one hour. Browser downloads go to your browser's configured download location; select a folder on E: if required.

## Input format

UTF-8 comma-separated CSV, one row per completed order:

```csv
customer_id,order_id,order_date,amount
C001,O001,2026-10-20,125.50
C001,O002,2026-10-25,70.00
C002,O003,2026-10-21,45.00
```

- Required columns: `customer_id`, `order_id`, `order_date`, `amount`.
- IDs are read as strings, preserving leading zeros.
- Dates must be ISO 8601 (prefer `YYYY-MM-DD`). Timestamps are normalized to UTC calendar days.
- Amounts must be finite positive numbers in a single currency, without currency symbols or thousands separators.
- Use order totals, not separate product lines. Conflicting entries for a customer/order pair are rejected; exact duplicates are removed.
- Invalid rows (missing IDs, invalid dates, nonpositive or invalid amounts) are removed and counted visibly.
- Refunds/returns are excluded, not subtracted. Monetary values describe positive completed purchases, not net revenue.
- Limits: 10 MB, 100,000 rows, and 20,000 customers. At least three customers and enough distinct RFM profiles are required; group count must be smaller than customer count.

## Method

- **Recency:** days since the customer's last order, relative to one day after the latest order by default. A custom reference date must not precede the latest order.
- **Frequency:** distinct order count per customer.
- **Monetary:** sum of positive order amounts per customer.
- Transform all three features with `log1p`, then standardize with population standard deviation. Constant features receive scale 1.
- Fit K-means with K-means++ initialization, 10 restarts, seed 42, and up to 100 iterations. Choose the run with lowest inertia and the requested number of nonempty groups.
- Number groups by descending mean spend. Profile descriptions compare group medians with the overall customer medians. These descriptions are not verified loyalty labels, and group numbers can change between analyses.
- The silhouette score uses Euclidean distance in transformed, standardized feature space. Up to 800 customers are sampled deterministically; singleton groups in that sample score zero. It is a separation metric, not classification accuracy. Compare segment sizes and business meaning alongside the score.
- The scatter chart displays at most 3,000 sampled customers for responsiveness; all valid customers participate in clustering and exports.

## Project structure

| File | Purpose |
| --- | --- |
| `app.py` | Web interface and cached analysis |
| `segmentation.py` | Validation, RFM aggregation, K-means, silhouette, CSV export |
| `generate_demo.py` | Deterministic synthetic order generator |
| `sample_orders.csv` | Ready-to-use synthetic demonstration data |
| `test_segmentation.py` | Data and model behavior tests |
| `test_app.py` | Streamlit interaction and upload tests |
| `.streamlit/config.toml` | Local server settings and theme |
| `requirements-lock.txt` | Exact installed dependency versions |
| `setup.ps1`, `run.ps1`, `Start App.cmd` | Installation and launch commands |

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest -v
.\.venv\Scripts\python.exe -m pip check
```

Optional development type checks:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m ty check app.py segmentation.py generate_demo.py
```

Dependencies are isolated in `.venv` and excluded from Git, along with caches and local reports. `requirements-lock.txt` allows reinstalling them. This is a learning app, not an automatic marketing decision system; use real business context when interpreting clusters.
