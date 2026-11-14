"""Validated RFM aggregation and reproducible K-means, implemented with NumPy."""
from io import BytesIO
import numpy as np
import pandas as pd

COLUMNS = ["customer_id", "order_id", "order_date", "amount"]
FEATURES = ["Recency", "Frequency", "Monetary"]

def read_orders(content: bytes):
    if len(content) > 10 * 1024 * 1024:
        raise ValueError("The CSV must be smaller than 10 MB.")
    try:
        raw = pd.read_csv(BytesIO(content), dtype=str, nrows=100001)
    except (ValueError, UnicodeError, pd.errors.ParserError) as exc:
        raise ValueError("Upload a valid UTF-8 CSV file with a header row.") from exc
    missing = set(COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
    if len(raw) > 100000:
        raise ValueError("Use at most 100,000 order rows.")
    df = raw[COLUMNS].copy()
    for col in ["customer_id", "order_id"]:
        df[col] = df[col].str.strip().replace("", pd.NA)
    df["order_date"] = pd.to_datetime(df["order_date"], format="ISO8601", errors="coerce", utc=True).dt.tz_convert(None).dt.normalize()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    valid = df.notna().all(axis=1) & np.isfinite(df["amount"]) & (df["amount"] > 0)
    clean = df.loc[valid].copy()
    invalid = len(df) - len(clean)
    duplicate = int(clean.duplicated().sum())
    clean = clean.drop_duplicates()
    if clean.duplicated(["customer_id", "order_id"]).any():
        raise ValueError("Conflicting rows for the same customer/order. Provide one total per order, not line items.")
    if clean.empty:
        raise ValueError("No valid positive-value orders remain after cleaning.")
    if clean["customer_id"].nunique() > 20000:
        raise ValueError("This learning app supports at most 20,000 customers.")
    return clean, {"input_rows": len(raw), "invalid_rows": invalid, "duplicate_rows": duplicate, "valid_orders": len(clean)}

def build_rfm(orders, reference=None):
    latest = orders["order_date"].max()
    if reference is not None:
        timestamp = pd.Timestamp(reference)
        if not isinstance(timestamp, pd.Timestamp):
            raise ValueError("Provide a valid reference date.")
        ref = timestamp.normalize()
    else:
        ref = latest + pd.Timedelta(days=1)
    if ref < latest:
        raise ValueError("The reference date cannot be earlier than the latest order.")
    grouped = orders.groupby("customer_id", sort=True)
    rfm = grouped.agg(last_order=("order_date", "max"), Frequency=("order_id", "nunique"), Monetary=("amount", "sum"))
    rfm["Recency"] = (ref - rfm.pop("last_order")).dt.days
    if not np.isfinite(rfm[FEATURES].to_numpy(dtype=float)).all():
        raise ValueError("Aggregated values are too large. Check order amounts.")
    return rfm[FEATURES].reset_index(), ref

def squared_distances(x, centers):
    return ((x[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)

def kmeans(x, k, seed=42, restarts=10):
    if not 2 <= k < len(x):
        raise ValueError("Choose at least two groups and fewer groups than customers.")
    if len(np.unique(x, axis=0)) < k:
        raise ValueError("There are fewer distinct customer profiles than requested groups. Reduce the group count.")
    rng = np.random.default_rng(seed)
    best = None
    for _ in range(restarts):
        centers = [x[rng.integers(len(x))]]
        for _ in range(1, k):
            d = squared_distances(x, np.asarray(centers)).min(axis=1)
            centers.append(x[rng.choice(len(x), p=d / d.sum())])
        centers = np.asarray(centers)
        for _ in range(100):
            distances = squared_distances(x, centers)
            labels = distances.argmin(axis=1)
            updated = np.asarray([x[labels == c].mean(axis=0) if np.any(labels == c) else x[np.argmax(distances.min(axis=1))] for c in range(k)])
            if np.allclose(updated, centers, rtol=0, atol=1e-6):
                centers = updated
                break
            centers = updated
        distances = squared_distances(x, centers)
        labels = distances.argmin(axis=1)
        inertia = float(distances[np.arange(len(x)), labels].sum())
        if len(np.unique(labels)) == k and (best is None or inertia < best[0]):
            best = inertia, labels, centers
    if best is None:
        raise ValueError("Could not form distinct groups. Try fewer groups.")
    return best

def silhouette(x, labels):
    # Deterministic sampled silhouette; at most 800 customers to bound memory.
    rng = np.random.default_rng(42)
    ix = rng.choice(len(x), min(800, len(x)), replace=False)
    sample, groups = x[ix], labels[ix]
    if len(np.unique(groups)) < 2:
        return None, len(ix)
    distances = np.sqrt(np.maximum(0, (sample ** 2).sum(axis=1)[:, None] + (sample ** 2).sum(axis=1)[None, :] - 2 * sample @ sample.T))
    np.fill_diagonal(distances, 0)
    scores = []
    for i, group in enumerate(groups):
        own = groups == group
        if own.sum() == 1:
            scores.append(0.0)
            continue
        a = distances[i, own].sum() / (own.sum() - 1)
        b = min(distances[i, groups == other].mean() for other in np.unique(groups) if other != group)
        scores.append((b - a) / max(a, b) if max(a, b) else 0)
    return float(np.mean(scores)), len(ix)

def segment(rfm, k):
    transformed = np.log1p(rfm[FEATURES].to_numpy(dtype=float))
    scale = transformed.std(axis=0)
    x = (transformed - transformed.mean(axis=0)) / np.where(scale > 0, scale, 1)
    inertia, labels, _ = kmeans(x, k)
    result = rfm.copy()
    # Stable display numbering ordered by mean spend; IDs are not ground-truth classes.
    order = sorted(range(k), key=lambda c: (-result.loc[labels == c, "Monetary"].mean(), c))
    result["Segment"] = [f"Group {order.index(int(c)) + 1}" for c in labels]
    summary = result.groupby("Segment", sort=True).agg(Customers=("customer_id", "size"), Recency=("Recency", "median"), Frequency=("Frequency", "median"), Monetary=("Monetary", "median"), Revenue=("Monetary", "sum")).reset_index()
    summary["Share (%)"] = (summary["Customers"] / len(result) * 100).round(1)
    global_med = result[FEATURES].median()
    def describe(row):
        return " / ".join(["More recent" if row["Recency"] <= global_med["Recency"] else "Less recent", "Frequent" if row["Frequency"] >= global_med["Frequency"] else "Occasional", "Higher spend" if row["Monetary"] >= global_med["Monetary"] else "Lower spend"])
    summary["Profile"] = summary.apply(describe, axis=1)
    score, sampled = silhouette(x, labels)
    return result, summary, {"silhouette": score, "silhouette_sample": sampled, "inertia": inertia, "customers": len(result), "groups": k, "seed": 42, "restarts": 10}

def csv_bytes(frame):
    safe = frame.copy()
    for name in safe.select_dtypes(include=["object", "string"]).columns:
        safe[name] = safe[name].map(lambda v: "'" + v if isinstance(v, str) and v.lstrip().startswith(("=", "+", "-", "@")) else v)
    return safe.to_csv(index=False).encode("utf-8-sig")
