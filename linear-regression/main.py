import math
import random
from statistics import mean


def predict(area, slope, intercept):
    return slope * area + intercept


def main():
    rng = random.Random(42)
    homes = [(area, 20_000 + 950 * area + rng.gauss(0, 8_000))
             for area in rng.choices(range(40, 201), k=200)]
    rng.shuffle(homes)
    train, test = homes[:160], homes[160:]

    area_mean = mean(area for area, _ in train)
    price_mean = mean(price for _, price in train)
    slope = sum((area - area_mean) * (price - price_mean)
                for area, price in train) / sum(
                    (area - area_mean) ** 2 for area, _ in train)
    intercept = price_mean - slope * area_mean

    errors = [price - predict(area, slope, intercept) for area, price in test]
    squared_error = sum(error ** 2 for error in errors)
    test_mean = mean(price for _, price in test)
    r2 = 1 - squared_error / sum((price - test_mean) ** 2 for _, price in test)

    print(f"Price = {intercept:,.2f} + {slope:,.2f} * area")
    print(f"Test MAE:  {mean(abs(error) for error in errors):,.2f}")
    print(f"Test RMSE: {math.sqrt(squared_error / len(test)):,.2f}")
    print(f"Test R^2:  {r2:.3f}")
    print(f"Predicted price for 120 m²: {predict(120, slope, intercept):,.2f}")


if __name__ == "__main__":
    main()
