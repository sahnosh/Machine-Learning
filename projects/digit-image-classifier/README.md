# Handwritten Digit Image Classification

## View the output

[Open the visual results report](https://sahnosh.github.io/Machine-Learning/) — includes sample images, actual/predicted digits, test accuracy, and the confusion matrix. This is a recorded evaluation report, not live inference.

Classify grayscale images of handwritten digits **0-9** with Python and scikit-learn. This small project demonstrates an end-to-end image classification workflow: load images, preprocess pixels, train a classifier, evaluate unseen images, and predict a sample.

## Dataset and method

- Dataset: scikit-learn's bundled [Digits dataset](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html), containing 1,797 images.
- Input: an **8 x 8 grayscale image**, with pixel intensities from **0 to 16**. Each image is flattened into 64 features.
- Target: one of ten digit classes (0 through 9).
- Split: 1,437 training images and 360 test images, stratified by class, seed 42.
- Model: StandardScaler followed by LogisticRegression. The scaler is fitted on the training images only.
- Baseline: a classifier that always predicts the most frequent training class.

The images are bundled with the library, so no separate dataset download or account is required after installing dependencies. This dataset originates from the UCI Optical Recognition of Handwritten Digits dataset; see the linked dataset documentation for source details.

## Setup

Requires Python **3.10 or newer**. Open a terminal in this project's folder (projects/digit-image-classifier), then install dependencies in your Python environment:

~~~sh
python -m pip install -r requirements.txt
~~~

Use a separate virtual environment if running alongside other Python projects.

## Run the demonstration

~~~sh
python digit_classifier.py
~~~

The script trains the model, prints evaluation metrics and a confusion matrix as JSON, and displays one held-out image as ASCII art. It then shows the actual digit, predicted digit, and probabilities for all ten classes. It does not save a model or create output files; training runs again each time.

For the confusion matrix, rows represent actual digits and columns represent predicted digits, ordered 0-9. The classification report includes precision, recall, F1, and support for each class.

## Classify your own small image

Prepare a comma-separated file containing exactly **8 rows and 8 columns** of numbers from 0 to 16, with dark background pixels near 0 and bright strokes near 16:

~~~sh
python digit_classifier.py --image-csv my-digit.csv
~~~

The script validates shape, pixel range, and finite values. This CSV represents the image pixels; it is not a filename list. Arbitrary JPEG/PNG photographs and full-size scanned documents are not supported by this teaching example.

## Tests

~~~sh
python -m unittest -v
~~~

Four tests check that training/test images do not overlap, preprocessing uses only training images, the held-out demo produces a valid prediction and probabilities, and malformed images are rejected.

## Verified example

Using Python 3.12 and scikit-learn 1.7.2 with seed 42:

| Measure | Result |
| --- | --- |
| Test accuracy | 97.22% (350 of 360 images) |
| Majority-class baseline | 10.00% |
| First held-out sample | Actual: 5; predicted: 5 |

This is one reproducible split, not a guarantee for new images. The dataset is small and low-resolution; external handwriting may differ substantially. Probabilities are model estimates, not guarantees. For further learning, compare models using cross-validation on the training set and keep test images for final evaluation.

## Files

- digit_classifier.py: training, evaluation, image validation, and prediction.
- test_digit_classifier.py: automated tests.
- requirements.txt: dependencies.

## خلاصهٔ دری

این پروژه ارقام دست‌نویس ۰ تا ۹ را از تصاویر خاکستری ۸×۸ تشخیص می‌دهد. پس از نصب وابستگی‌ها، دستور python digit_classifier.py را اجرا کنید. نتیجهٔ ارزیابی، تصویر نمونه به شکل متنی و رقم پیش‌بینی‌شده نمایش داده می‌شود. تصاویر باید مقدار پیکسل بین ۰ تا ۱۶ داشته باشند. این نمونه برای آموزش است و عکس‌های عادی JPEG یا PNG را مستقیماً پردازش نمی‌کند.
