"""User-based collaborative filtering with a popularity fallback."""
from pathlib import Path
import argparse
import csv
import json
import numpy as np

ROOT = Path(__file__).resolve().parent

def load_data():
    try:
        with (ROOT / "data/movies.csv").open(encoding="utf-8", newline="") as handle:
            movies = {int(r["movieId"]): r for r in csv.DictReader(handle)}
        with (ROOT / "data/ratings.csv").open(encoding="utf-8", newline="") as handle:
            ratings = [(int(r["userId"]), int(r["movieId"]), float(r["rating"]), int(r["timestamp"])) for r in csv.DictReader(handle)]
    except FileNotFoundError:
        raise SystemExit("Dataset missing. Run .venv\\Scripts\\python.exe download_data.py first.")
    return movies, ratings

class Recommender:
    def __init__(self, movies, ratings):
        self.movies = movies
        self.ids = sorted(movies)
        self.item_index = {mid: i for i, mid in enumerate(self.ids)}
        self.users = sorted({r[0] for r in ratings})
        self.user_index = {uid: i for i, uid in enumerate(self.users)}
        self.matrix = np.zeros((len(self.users), len(self.ids)), dtype=np.float64)
        for uid, mid, rating, _ in ratings:
            self.matrix[self.user_index[uid], self.item_index[mid]] = rating
        norms = np.linalg.norm(self.matrix, axis=1, keepdims=True)
        self.normalized = self.matrix / np.maximum(norms, 1e-12)
        counts = (self.matrix > 0).sum(axis=0)
        sums = self.matrix.sum(axis=0)
        mean = sums.sum() / max(counts.sum(), 1)
        # Bayesian shrinkage: ten prior ratings at the global average.
        self.popularity = (sums + 10 * mean) / (counts + 10)
        self.popularity[counts == 0] = -np.inf

    def recommend(self, user_id, n=10, neighbors=30, popular_only=False):
        if n < 1 or neighbors < 1:
            raise ValueError("n and neighbors must be positive")
        scores = self.popularity.copy()
        seen = np.array([], dtype=int)
        if user_id in self.user_index:
            row = self.user_index[user_id]
            seen = np.flatnonzero(self.matrix[row])
            if not popular_only:
                similarities = self.normalized @ self.normalized[row]
                similarities[row] = 0
                nearest = np.argsort(-similarities, kind="stable")[:neighbors]
                nearest = nearest[similarities[nearest] > 0]
                if len(nearest):
                    weights = similarities[nearest]
                    values = self.matrix[nearest]
                    numerator = np.asarray(values.T @ weights).ravel()
                    denominator = np.asarray((values > 0).T @ weights).ravel()
                    # Shrink estimates toward the baseline for sparse evidence.
                    prior = np.where(np.isfinite(scores), scores, 0)
                    scores = (numerator + 3 * prior) / (denominator + 3)
                    scores[~np.isfinite(self.popularity)] = -np.inf
        scores[seen] = -np.inf
        order = np.argsort(-scores, kind="stable")
        return [(self.ids[i], float(scores[i])) for i in order if np.isfinite(scores[i])][:n]

def evaluate(movies, ratings):
    groups = {}
    for rating in ratings:
        groups.setdefault(rating[0], []).append(rating)
    train, held_out = [], {}
    for uid, rows in groups.items():
        rows.sort(key=lambda r: (r[3], r[1]))
        split = max(1, int(len(rows) * .8))
        train.extend(rows[:split])
        relevant = {r[1] for r in rows[split:] if r[2] >= 4}
        if relevant:
            held_out[uid] = relevant
    model = Recommender(movies, train)
    output = {"split": "earliest 80% per user for training; latest 20% for test", "relevance": "test rating >= 4", "evaluated_users": len(held_out), "train_ratings": len(train), "note": "Per-user temporal split; not a global time cutoff. Unseen training items count as misses. Scores are ranking estimates, not probabilities."}
    for label, baseline in (("collaborative", False), ("popularity", True)):
        recalls, precisions, hits = [], [], []
        for uid, relevant in held_out.items():
            predicted = {mid for mid, _ in model.recommend(uid, popular_only=baseline)}
            hit = len(predicted & relevant)
            recalls.append(hit / len(relevant))
            precisions.append(hit / 10)
            hits.append(float(hit > 0))
        output[label] = {"recall_at_10": float(np.mean(recalls)), "precision_at_10": float(np.mean(precisions)), "hit_rate_at_10": float(np.mean(hits))}
    path = ROOT / "reports"
    path.mkdir(exist_ok=True)
    (path / "evaluation.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("search")
    search.add_argument("query")
    recommend = sub.add_parser("recommend")
    recommend.add_argument("--user", type=int, default=1)
    recommend.add_argument("--top", type=int, default=10)
    recommend.add_argument("--popular", action="store_true")
    sub.add_parser("evaluate")
    sub.add_parser("stats")
    args = parser.parse_args()
    movies, ratings = load_data()
    if args.command == "search":
        found = [r for r in movies.values() if args.query.casefold() in r["title"].casefold()]
        for r in found[:30]:
            print(r["movieId"], r["title"], "|", r["genres"])
        print(f"{len(found)} matches; showing at most 30.")
    elif args.command == "stats":
        print(f"Movies: {len(movies):,}; ratings: {len(ratings):,}; users: {len({r[0] for r in ratings}):,}")
    elif args.command == "evaluate":
        evaluate(movies, ratings)
    else:
        model = Recommender(movies, ratings)
        if args.user not in model.user_index:
            print("Unknown user: showing popularity recommendations.")
        for mid, score in model.recommend(args.user, n=args.top, popular_only=args.popular):
            print(f"{mid:6} | {score:.3f} | {movies[mid]['title']}")

if __name__ == "__main__":
    main()
