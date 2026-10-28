import tempfile
import unittest
from pathlib import Path

import joblib
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from iris_classifier import SEED, predict, train


class ClassifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle, cls.metrics = train()

    def test_held_out_evaluation_beats_baseline(self):
        self.assertEqual(self.metrics["train_samples"], 120)
        self.assertEqual(self.metrics["test_samples"], 30)
        self.assertGreater(self.metrics["accuracy"], self.metrics["baseline_accuracy"])
        self.assertEqual(sum(map(sum, self.metrics["confusion_matrix"])), 30)

    def test_scaler_fits_training_data_only(self):
        data = load_iris()
        x_train, _, _, _ = train_test_split(
            data.data, data.target, test_size=0.2, random_state=SEED,
            stratify=data.target,
        )
        np.testing.assert_allclose(
            self.bundle["model"].named_steps["standardscaler"].mean_,
            x_train.mean(axis=0),
        )

    def test_saved_model_predicts_after_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.joblib"
            joblib.dump(self.bundle, path)
            result = predict(joblib.load(path), [5.1, 3.5, 1.4, 0.2])
        self.assertEqual(result["species"], "setosa")
        self.assertAlmostEqual(sum(result["probabilities"].values()), 1.0, places=5)

    def test_rejects_invalid_measurements(self):
        for features in ([1, 2, 3], [0, 1, 2, 3], [-1, 1, 2, 3],
                         [float("nan"), 1, 2, 3], [float("inf"), 1, 2, 3]):
            with self.subTest(features=features), self.assertRaises(ValueError):
                predict(self.bundle, features)


if __name__ == "__main__":
    unittest.main()
