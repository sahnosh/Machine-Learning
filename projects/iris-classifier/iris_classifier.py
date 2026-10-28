"""Train and use a small, reproducible Iris classifier. Measurements are in cm."""

import argparse
import json
import math
from pathlib import Path

import joblib
import sklearn
from sklearn.datasets import load_iris
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ARTIFACTS = Path(__file__).resolve().parent / "artifacts"
SEED = 42


def train():
    """Keep the stratified test set separate from model fitting and scaling."""
    iris = load_iris()
    x_train, x_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=SEED,
        stratify=iris.target,
    )
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    baseline = DummyClassifier(strategy="most_frequent").fit(x_train, y_train)
    names = iris.target_names.tolist()
    metrics = {
        "dataset": "scikit-learn Iris",
        "scikit_learn_version": sklearn.__version__,
        "random_seed": SEED,
        "train_samples": len(y_train),
        "test_samples": len(y_test),
        "accuracy": float(accuracy_score(y_test, predictions)),
        "baseline_accuracy": float(baseline.score(x_test, y_test)),
        "class_names": names,
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        "classification_report": classification_report(
            y_test, predictions, target_names=names, output_dict=True,
            zero_division=0,
        ),
    }
    bundle = {
        "model": model, "class_names": names,
        "feature_names": iris.feature_names,
        "scikit_learn_version": sklearn.__version__,
    }
    return bundle, metrics


def predict(bundle, features):
    """Validate four finite, positive measurements before making a prediction."""
    if len(features) != 4 or any(not math.isfinite(x) or x <= 0 for x in features):
        raise ValueError("Provide exactly four finite, positive measurements in centimeters.")
    model = bundle["model"]
    probabilities = model.predict_proba([features])[0]
    index = int(model.predict([features])[0])
    return {
        "species": bundle["class_names"][index],
        "probabilities": {
            bundle["class_names"][int(label)]: round(float(probability), 6)
            for label, probability in zip(model.classes_, probabilities)
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    training = commands.add_parser("train", help="Train, evaluate, and save a model")
    training.add_argument("--output-dir", type=Path, default=ARTIFACTS)
    prediction = commands.add_parser("predict", help="Predict using a model you trained")
    prediction.add_argument("--model", type=Path, default=ARTIFACTS / "model.joblib")
    prediction.add_argument("--features", type=float, nargs=4, required=True,
                            metavar=("SEPAL_LENGTH", "SEPAL_WIDTH", "PETAL_LENGTH", "PETAL_WIDTH"))
    args = parser.parse_args()
    if args.command == "train":
        bundle, metrics = train()
        args.output_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(bundle, args.output_dir / "model.joblib")
        (args.output_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2) + "\n", encoding="utf-8",
        )
        print(f"Training samples: {metrics['train_samples']}; test samples: {metrics['test_samples']}")
        print(f"Test accuracy: {metrics['accuracy']:.2%}")
        print(f"Baseline accuracy: {metrics['baseline_accuracy']:.2%}")
        print("Confusion matrix (rows: actual, columns: predicted):")
        for row in metrics["confusion_matrix"]:
            print(row)
        print(f"Model and evaluation saved to {args.output_dir}")
    else:
        if not args.model.is_file():
            parser.error("Model not found. Run 'python iris_classifier.py train' first.")
        # joblib files must only be loaded from trusted sources.
        bundle = joblib.load(args.model)
        try:
            result = predict(bundle, args.features)
        except ValueError as error:
            parser.error(str(error))
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
