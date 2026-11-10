# SMS Spam Detection

A machine learning project that classifies English SMS messages as **spam** (unwanted messages) or **ham** (normal messages). It includes a desktop interface, command-line prediction, model training, evaluation reports, and automated tests.

## Install from GitHub

On Windows, install Python 3.11 with the Python Launcher and Git. Clone the repository to drive E, then run the setup script from the project folder:

```powershell
git clone https://github.com/sahnosh/Machine-Learning.git E:\Machine-Learning
cd E:\Machine-Learning\SpamDetection
.\setup.cmd
.\run.cmd
```

`setup.cmd` creates a virtual environment, installs the pinned dependencies, downloads the public UCI dataset, and trains the model. Internet access is required for the initial package and dataset downloads.

The repository contains source code, dataset attribution, tests, and evaluation reports. Raw data, the trained model, the Python runtime, and installed packages are kept locally and are recreated or downloaded during setup.

### Original local installation

The original installation is located at `E:\SpamDetection`. Its standalone Python runtime, virtual environment, dependencies, package cache, and temporary files are all on drive E. It also includes a `wheelhouse` folder for offline package installation.

A fresh GitHub clone creates its virtual environment and cache inside the project folder and uses your installed Python 3.11 as the base interpreter unless a local `runtime\python.exe` is available. Offline setup requires both the downloaded dataset and all required package wheels to be available locally.

### Manual setup

From the project folder, using Python 3.11:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe spam_detector.py train
.\.venv\Scripts\python.exe gui.py
```

## Usage

After setup, double-click `run.cmd` and enter an English message in the desktop interface. To retrain the model, run `train.cmd`.

For command-line prediction, run these commands from the project folder:

```powershell
.\run_cli.cmd predict "Congratulations! You have won a free prize. Call now to claim!"
.\run_cli.cmd predict "Can we meet tomorrow for lunch?"
.\run_cli.cmd train
```

Training and prediction run locally after the initial downloads. Messages entered for prediction are not sent over the internet.

## Dataset and training method

The project uses the UCI SMS Spam Collection. Dataset attribution, source links, and license information are recorded in [data/SOURCE.md](data/SOURCE.md).

1. Normalize case and whitespace to identify duplicate messages.
2. Remove duplicate messages and groups with conflicting labels.
3. Split the remaining data into stratified training and test sets: 80% training and 20% testing, with `random_state=42`.
4. Fit a TF-IDF vectorizer with word unigrams and bigrams on the training set only.
5. Train a Multinomial Naive Bayes classifier with `alpha=0.1`.
6. Evaluate on the held-out test set and save the evaluated model.

The saved model is trained only on the training split. Test messages are not used to fit the vocabulary or classifier. This split does not necessarily separate near-duplicate messages and does not replace evaluation on new, real-world messages.

## Evaluation results

The initial run used 5,159 unique, non-conflicting messages: 4,127 for training and 1,032 for testing.

| Metric | Result |
| --- | ---: |
| Overall accuracy | 98.26% |
| Spam precision | 98.25% |
| Spam recall | 87.50% |
| Spam F1 score | 92.56% |

The test set contained 904 normal messages and 128 spam messages. The model correctly identified 112 spam messages, missed 16 spam messages, and incorrectly flagged 2 normal messages as spam.

Full results are available in [reports/metrics.json](reports/metrics.json) and [reports/evaluation.txt](reports/evaluation.txt). In the confusion matrix, rows represent actual labels and columns represent predicted labels, in the order `ham`, `spam`.

## Project files

| Path | Purpose |
| --- | --- |
| `spam_detector.py` | Dataset download, cleaning, training, evaluation, and prediction |
| `gui.py` | Local desktop interface |
| `data/SOURCE.md` | Dataset attribution and license information |
| `data/SMSSpamCollection` | Downloaded dataset; generated locally |
| `models/spam_model.joblib` | Trained model; generated locally |
| `reports/metrics.json` | Accuracy, precision, recall, F1, and confusion matrix |
| `reports/evaluation.txt` | Human-readable evaluation report |
| `reports/test_predictions.csv` | Test-set predictions; generated locally |
| `reports/validation.txt` | Recorded validation results |
| `tests/test_pipeline.py` | Automated tests |
| `requirements.txt` / `requirements-lock.txt` | Pinned dependency versions |
| `setup.cmd` | Environment setup and model training |
| `environment.cmd` | Project-local environment settings |
| `run.cmd` / `run_cli.cmd` | Desktop and command-line launchers |
| `train.cmd` / `test.cmd` | Training and test launchers |
| `.venv/` | Local virtual environment and installed dependencies |
| `runtime/` | Standalone Python and its license in the original installation |
| `wheelhouse/` | Local package wheels for offline installation |
| `cache/` / `tmp/` | Project-local cache and temporary files |

## Tests

Run `test.cmd`, or execute:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The original installation passed all four automated tests, the dependency compatibility check, and desktop button checks with spam and ham examples. The drive-E isolation test applies to the original installation with its standalone runtime and is skipped in a fresh clone without that runtime.

## Train with your own data

Create a UTF-8 text file without a header. Each row must contain a label (`ham` or `spam`), a tab character, and a nonempty message:

```text
ham	Can we meet tomorrow for lunch?
spam	Congratulations! Claim your free prize now!
```

The separators above are actual tab characters. Provide enough examples of both labels for the stratified train/test split, then run:

```powershell
.\run_cli.cmd train --data "E:\path\to\messages.tsv"
```

Training replaces the saved model and evaluation reports.

## Limitations

- The model is trained on English SMS messages. Dari/Persian performance has not been evaluated and requires suitable labeled training data.
- The spam score is not a calibrated probability, and predictions can be incorrect.
- Load only trusted `joblib` model files created by this project.
- The original standalone runtime is Python 3.11.1, copied from the existing installation. Use an updated, supported Python release for production deployment and verify dependency compatibility.
