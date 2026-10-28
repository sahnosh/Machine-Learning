# Iris Flower Classifier

A small Python project that predicts **setosa**, **versicolor**, or **virginica** from four flower measurements. Learn a complete workflow: load data, split it, train a model, evaluate it, save it, and predict a new sample.

## Setup

Python **3.10 or newer** is required. From the repository root:

```sh
cd projects/iris-classifier
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```sh
# macOS / Linux
source .venv/bin/activate
```

Then install dependencies:

```sh
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use `.venv\Scripts\python.exe` instead of `python` in the commands below. No change to your system execution policy is needed.

## Train and evaluate

```sh
python iris_classifier.py train
```

The dataset is bundled with scikit-learn; no dataset account or download is required after installation. There are 150 samples, four features, and three equally represented species. A stratified split reserves **30 samples for testing** and uses **120 for training**, with seed 42.

The pipeline combines `StandardScaler` and `LogisticRegression`. Scaling is fitted only on training data. Evaluation includes test accuracy, a majority-class baseline, a confusion matrix, and per-class precision, recall, and F1 scores. Rows of the confusion matrix are actual classes, columns are predicted classes, in the order `setosa`, `versicolor`, `virginica`.

Generated files (excluded from Git):

- `artifacts/model.joblib`: the trained pipeline, feature names, class names, and library version.
- `artifacts/metrics.json`: the evaluation results and run settings.

Use `--output-dir PATH` to choose a different output folder. Only load model files you trained or otherwise trust: joblib files can execute code when loaded. Use the same dependency versions when reloading a saved model.

### Verified example result

With Python 3.12 and scikit-learn 1.7.2, seed 42 produced **93.33% test accuracy** (28 of 30 correct), compared with **33.33%** for the majority-class baseline:

```text
                 Predicted
                 setosa  versicolor  virginica
Actual setosa       10       0           0
Actual versicolor    0       9           1
Actual virginica     0       1           9
```

This is an example run on one fixed split, not a guarantee for other datasets or configurations.

## Predict a flower

Measurements must be positive, finite numbers in **centimeters**, in this order:

1. Sepal length
2. Sepal width
3. Petal length
4. Petal width

```sh
python iris_classifier.py predict --features 5.1 3.5 1.4 0.2
```

This example predicts `setosa` and prints probabilities for all three species. Use `--model PATH` to select a model stored elsewhere. Run `python iris_classifier.py --help` for command help.

## Tests

```sh
python -m unittest -v
```

Tests cover evaluation against the baseline, fitting the scaler without test-data leakage, saving/reloading the model, and rejecting invalid measurements.

## What to learn next

Try cross-validation on the training data or compare another classifier. Keep the held-out test set for the final evaluation. Iris is a small teaching dataset: one test split is not evidence of real-world performance, and prediction probabilities are not guarantees.

## References

- [scikit-learn Iris dataset](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html)
- [scikit-learn pipelines and evaluation](https://scikit-learn.org/stable/getting_started.html)

## راهنمای کوتاه دری

این پروژه با استفاده از چهار اندازهٔ گل، نوع گل Iris را پیش‌بینی می‌کند. نخست وابستگی‌ها را نصب کنید، سپس با دستور `python iris_classifier.py train` مدل را آموزش دهید. برای پیش‌بینی، دستور نمونهٔ بالا را اجرا کنید. تمام اندازه‌ها باید به سانتی‌متر و به ترتیب طول و عرض کاسبرگ، سپس طول و عرض گلبرگ باشند. نتیجه برای آموزش و تمرین است.
