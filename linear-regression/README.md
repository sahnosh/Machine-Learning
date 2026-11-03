# House Price Prediction with Linear Regression

This Python project uses simple linear regression to estimate a house's price from its floor area in square meters. Prices are expressed in fictional currency units.

## Run the project

Run the following command from the project folder. The project uses only the Python 3 standard library.

```bash
python main.py
```

## How it works

1. Generate 200 synthetic house records with a linear relationship between area and price plus random noise.
2. Shuffle the records with a fixed random seed and split them into 160 training and 40 test records.
3. Fit the slope and intercept by ordinary least squares on the training records.
4. Evaluate the model on the test records and predict the price of a 120 m² house.

## Example results

| Metric | Test result |
| --- | ---: |
| Mean absolute error (MAE) | 6,567.77 |
| Root mean squared error (RMSE) | 8,575.96 |
| Coefficient of determination (R²) | 0.966 |

MAE reports the average absolute prediction error in price units. RMSE uses the same units and gives more weight to large errors. R² compares the model's squared error with the squared error of a constant prediction equal to the mean test price.

The example prediction for 120 m² is 134,296.94 fictional currency units. These results describe the synthetic dataset used in this exercise.
