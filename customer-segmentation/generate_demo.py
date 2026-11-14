"""Generate deterministic synthetic order-level data; no real customers."""
from pathlib import Path
from datetime import date, timedelta
import numpy as np
import pandas as pd

def generate():
    rng = np.random.default_rng(42)
    end = date(2026, 10, 31)
    rows = []
    for i in range(1, 401):
        style = (i - 1) // 100
        n = int(rng.integers(*[(12, 25), (2, 7), (5, 13), (1, 4)][style]))
        recent = int(rng.integers(*[(0, 20), (0, 35), (100, 220), (50, 180)][style]))
        for j in range(n):
            days = recent if j == 0 else recent + int(rng.integers(1, 140))
            rows.append((f"C{i:04d}", f"O{i:04d}-{j:02d}", (end - timedelta(days=days)).isoformat(), round(float(rng.lognormal([4.5, 3.5, 4.0, 3.0][style], .35)), 2)))
    return pd.DataFrame(dict(zip(["customer_id", "order_id", "order_date", "amount"], zip(*rows))))

if __name__ == "__main__":
    path = Path(__file__).with_name("sample_orders.csv")
    generate().to_csv(path, index=False)
    print("Created", path)
