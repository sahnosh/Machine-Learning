# Movie Recommendation System

An educational command-line recommender built with Python and NumPy using the MovieLens small dataset. It recommends unseen movies for existing dataset users and compares user-based collaborative filtering against a popularity baseline.

## Requirements

- Windows PowerShell
- Python 3.11 (the version used to test this project), available as `python`
- Internet access for the first setup

NumPy is the only external runtime dependency. Exact installed versions are recorded in `requirements-lock.txt`.

## Setup

From the repository root:

```powershell
cd movie-recommender
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
```

The setup script creates `.venv`, installs dependencies, saves offline installation packages in `wheelhouse`, and downloads MovieLens from its official publisher. Installer cache and temporary files stay in `.cache` and `.tmp` inside the project.

For the original local installation, the project directory is `E:\Machine-Learning\movie-recommender`. The virtual environment uses the existing system Python interpreter; the base interpreter is not bundled with this repository.

## Run

Run these commands from the `movie-recommender` directory:

```powershell
# Recommend movies for dataset user 1 (default).
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1

# Inspect dataset size.
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 stats

# Search movie titles.
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 search "Toy Story"

# Recommend ten movies for dataset user 5.
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 recommend --user 5 --top 10

# Compare against the popularity baseline.
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 recommend --user 5 --popular

# Evaluate both methods and save a report.
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 evaluate

# Run the automated tests.
.\.venv\Scripts\python.exe -m unittest -v
```

User IDs identify anonymous users in MovieLens, not personal accounts. Unknown users receive popularity recommendations. This version has a command-line interface; entering a new personal rating profile and a graphical interface are not implemented.

## How it works

1. Load movie metadata and user ratings.
2. Build a user-by-movie rating matrix, using zero for missing ratings.
3. Calculate a popularity baseline: each movie's average is shrunk toward the global average with a prior equivalent to ten ratings.
4. Calculate cosine similarity between users and select up to 30 neighbors with positive similarity.
5. Combine their ratings using similarity weights and shrink estimates toward the popularity baseline with weight 3.
6. Exclude movies the target user has already rated and movies with no training ratings, then return the highest-ranked results.

Recommendation scores are ranking estimates, not probabilities. The dense matrix is suitable for this small educational dataset; larger datasets should use sparse storage and more scalable retrieval.

## Evaluation

For each user, the earliest 80% of ratings are used for training and the latest 20% for testing. Test ratings of 4 or higher are treated as relevant. Users with no relevant test movies are excluded from the metric averages. This is a per-user temporal split, not a shared global time cutoff. Relevant items unseen during training count as misses.

The saved run in `reports/evaluation.json` evaluates 592 users with 80,419 training ratings:

| Method | Recall@10 | Precision@10 | Hit rate@10 |
| --- | ---: | ---: | ---: |
| Collaborative filtering | 0.0481 | 0.0544 | 0.3395 |
| Popularity baseline | 0.0324 | 0.0444 | 0.2736 |

Recall measures the fraction of relevant test movies retrieved. Precision measures the relevant fraction of the ten recommendation slots. Hit rate measures the fraction of users receiving at least one relevant recommendation. Results are an initial learning baseline, not a guarantee of recommendation quality or performance on other datasets.

## Project files

| Path | Purpose |
| --- | --- |
| `recommender.py` | Data loading, recommendation model, CLI, and evaluation |
| `download_data.py` | Official dataset download and SHA-256 provenance record |
| `test_recommender.py` | Tests for exclusions, ranking, unknown users, and input validation |
| `setup.ps1` | Local environment, dependency, and data setup |
| `run.ps1` | PowerShell launcher |
| `requirements.txt` | Supported dependency range |
| `requirements-lock.txt` | Exact dependency versions used locally |
| `reports/evaluation.json` | Saved evaluation results |
| `data/` | Downloaded dataset, archive, source metadata, and publisher README |
| `.venv/` | Local Python environment and installed packages |
| `wheelhouse/` | Offline installation packages for a compatible Python/Windows environment |
| `.cache/`, `.tmp/` | Local installation cache and temporary files |

Downloaded data, virtual environments, caches, and package binaries are excluded from Git. Run setup after cloning to recreate them.

## Offline dependency installation

After a successful online setup, the saved packages can be reused on a compatible Python/Windows environment:

```powershell
.\.venv\Scripts\python.exe -m pip install --no-index --find-links wheelhouse -r requirements-lock.txt
```

This command installs dependencies only. Keep the downloaded `data` directory for offline recommendation runs; it does not download missing data or bundle Python itself.

## Data and references

- [MovieLens small dataset and download information](https://grouplens.org/datasets/movielens/latest/)
- [MovieLens dataset documentation and usage conditions](https://files.grouplens.org/datasets/movielens/ml-latest-small-README.html)
- [NumPy documentation](https://numpy.org/doc/stable/)

The dataset is provided by GroupLens. Review the publisher's usage conditions in `data/README.txt` before reusing or redistributing it. `data/source.json` records the download URL and archive SHA-256.
