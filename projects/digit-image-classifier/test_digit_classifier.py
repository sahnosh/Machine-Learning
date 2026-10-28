import unittest

import numpy as np

from digit_classifier import predict_image, render_ascii, train, validate_image


class DigitClassifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, cls.metrics, cls.data, cls.train_ids, cls.test_ids = train()

    def test_evaluation_uses_separate_images_and_beats_baseline(self):
        self.assertTrue(set(self.train_ids).isdisjoint(self.test_ids))
        self.assertEqual(len(self.train_ids) + len(self.test_ids), 1797)
        self.assertEqual(self.metrics["test_samples"], 360)
        self.assertGreater(self.metrics["accuracy"], self.metrics["baseline_accuracy"])
        self.assertEqual(sum(map(sum, self.metrics["confusion_matrix"])), 360)

    def test_scaler_uses_training_images_only(self):
        expected = self.data.data[self.train_ids].mean(axis=0)
        actual = self.model.named_steps["standardscaler"].mean_
        np.testing.assert_allclose(actual, expected)

    def test_held_out_demo_and_probability_output(self):
        index = int(self.test_ids[0])
        result = predict_image(self.model, self.data.images[index])
        self.assertEqual(result["digit"], int(self.data.target[index]))
        self.assertEqual(set(result["probabilities"]), set(map(str, range(10))))
        self.assertAlmostEqual(sum(result["probabilities"].values()), 1.0, places=5)
        self.assertEqual(len(render_ascii(self.data.images[index]).splitlines()), 8)

    def test_invalid_images_are_rejected(self):
        invalid = [np.zeros((7, 8)), np.zeros(64), np.full((8, 8), -1),
                   np.full((8, 8), 17), np.full((8, 8), np.nan),
                   np.full((8, 8), np.inf)]
        for image in invalid:
            with self.subTest(shape=image.shape), self.assertRaises(ValueError):
                validate_image(image)


if __name__ == "__main__":
    unittest.main()
