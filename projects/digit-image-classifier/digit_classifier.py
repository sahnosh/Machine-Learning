"""Classify 8x8 grayscale handwritten digit images using scikit-learn."""
import argparse
import json

import numpy as np
from sklearn.datasets import load_digits
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SEED = 42


def validate_image(image):
    """Accept an 8x8 grayscale image with finite pixel intensities from 0 to 16."""
    pixels = np.asarray(image, dtype=float)
    if pixels.shape != (8, 8):
        raise ValueError("Expected an 8x8 image (8 rows and 8 columns).")
    if not np.isfinite(pixels).all() or (pixels < 0).any() or (pixels > 16).any():
        raise ValueError("Pixels must be finite numbers between 0 and 16.")
    return pixels.reshape(1, 64)


def train():
    """Fit on training images only; reserve a stratified 20% test set."""
    digits = load_digits()
    train_ids, test_ids = train_test_split(
        np.arange(len(digits.target)), test_size=0.2,
        random_state=SEED, stratify=digits.target,
    )
    x_train, x_test = digits.data[train_ids], digits.data[test_ids]
    y_train, y_test = digits.target[train_ids], digits.target[test_ids]
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    model.fit(x_train, y_train)
    predicted = model.predict(x_test)
    baseline = DummyClassifier(strategy="most_frequent").fit(x_train, y_train)
    metrics = {
        "seed": SEED,
        "train_samples": len(train_ids),
        "test_samples": len(test_ids),
        "accuracy": float(accuracy_score(y_test, predicted)),
        "baseline_accuracy": float(baseline.score(x_test, y_test)),
        "confusion_matrix": confusion_matrix(y_test, predicted).tolist(),
        "classification_report": classification_report(
            y_test, predicted, output_dict=True, zero_division=0,
        ),
    }
    return model, metrics, digits, train_ids, test_ids


def predict_image(model, image):
    features = validate_image(image)
    probabilities = model.predict_proba(features)[0]
    return {
        "digit": int(model.predict(features)[0]),
        "probabilities": {
            str(int(label)): round(float(probability), 6)
            for label, probability in zip(model.classes_, probabilities)
        },
    }


def render_ascii(image):
    shades = " .:-=+*#%@"
    return "\n".join(
        "".join(shades[round(float(pixel) / 16 * 9)] for pixel in row)
        for row in np.asarray(image)
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image-csv", help="Optional CSV with 8 rows of 8 pixel values (0-16)")
    args = parser.parse_args()
    model, metrics, digits, _, test_ids = train()
    print("Evaluation (held-out images):")
    print(json.dumps(metrics, indent=2))
    if args.image_csv:
        try:
            image = np.loadtxt(args.image_csv, delimiter=",")
            result = predict_image(model, image)
        except (OSError, ValueError) as error:
            parser.error(str(error))
    else:
        index = int(test_ids[0])
        image = digits.images[index]
        result = predict_image(model, image)
        print(f"Demo image: held-out dataset index {index}; actual digit: {digits.target[index]}")
    print(render_ascii(image))
    print("Prediction:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
