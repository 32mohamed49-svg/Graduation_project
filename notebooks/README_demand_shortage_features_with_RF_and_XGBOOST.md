# Demand Shortage Prediction

A machine learning project that predicts whether a product is facing an **urgent shortage crisis** using demand, inventory, sales, and supplier-related features.

The notebook compares **Random Forest** and **XGBoost**, tunes the XGBoost model with cross-validation, analyzes feature importance, and saves the selected model for reuse.

## Project Objective

The goal is to identify urgent product-shortage situations early enough to support better inventory and supply-chain decisions.

This is a **binary classification** task:

| Target value | Meaning |
|---|---|
| `0` | No urgent shortage crisis |
| `1` | Urgent shortage crisis |

## Dataset

The project uses `demand_shortage_features.csv`.

- **Rows:** 600
- **Columns:** 15
- **Target:** `urgent_shortage_flag`
- **Target distribution:**
  - Class 0: 324 records (~54%)
  - Class 1: 276 records (~46%)

The notebook's initial data checks found no missing values and no duplicate rows.

### Main feature groups

- Sales: `mfg_units_sold_total`, `mfg_units_sold_mean`
- Inventory: `mfg_avg_inventory`, `mfg_avg_days_cover`, `mfg_avg_inv_vs_rop`
- Reorder-point behavior: `mfg_below_rop_rate`
- Supplier operations: `mfg_avg_lead_time`
- Demand and promotions: `mfg_avg_forecast`, `mfg_promo_rate`
- Time: `year`, `month`

## Workflow

1. **Data loading and inspection**
   - Loaded the CSV with Pandas.
   - Checked dimensions, data types, missing values, duplicates, descriptive statistics, and target distribution.

2. **Data cleaning and feature selection**
   - Removed `SKU_Code`, `year_month`, and `stockout_risk_flag`.
   - Removed `mfg_avg_forecast` after the notebook's correlation analysis identified a perfect positive correlation with `mfg_units_sold_mean`.
   - Kept `urgent_shortage_flag` as the prediction target.

3. **Exploratory Data Analysis (EDA)**
   - Examined feature distributions and relationships.
   - Reviewed correlations to understand relationships with the target and identify redundant information.

4. **Train-test split**
   - 80% training data and 20% testing data.
   - Used `random_state=42` and `stratify=y`.

5. **Preprocessing**
   - Applied `StandardScaler` to numerical features.
   - Configured `OneHotEncoder` for categorical features.
   - Combined preprocessing and classification in Scikit-learn Pipelines.

6. **Model training and comparison**
   - Trained a Random Forest classifier.
   - Trained an XGBoost classifier.
   - Evaluated accuracy, classification metrics, and the XGBoost confusion matrix.

7. **Hyperparameter tuning**
   - Applied `GridSearchCV` to the XGBoost pipeline.
   - Used 5-fold cross-validation and accuracy as the scoring metric.

8. **Feature importance and prediction verification**
   - Ranked the features used by the tuned XGBoost model.
   - Tested a sample prediction and its estimated shortage probability.

9. **Model persistence**
   - Saved the tuned pipeline as `best_xgb_disruption_model.joblib`.

## Model Results

All results below are taken from the notebook outputs.

| Model | Training Accuracy | Test Accuracy |
|---|---:|---:|
| Random Forest | 100.00% | 97.50% |
| Baseline XGBoost | 100.00% | 97.50% |
| Tuned XGBoost | 99.79% | 97.50% |

### Tuned XGBoost

- **Best 5-fold cross-validation accuracy:** 98.12%
- **Test accuracy:** 97.50%

Best hyperparameters:

```python
{
    "classifier__learning_rate": 0.05,
    "classifier__max_depth": 3,
    "classifier__min_child_weight": 3,
    "classifier__n_estimators": 100,
    "classifier__subsample": 0.8
}
```

Test confusion matrix (rows = actual class, columns = predicted class):

```text
[[63, 2],
 [ 1, 54]]
```

The test set contained 120 records: 65 from class 0 and 55 from class 1.

## Feature Importance

The tuned XGBoost model reported the following leading features:

| Feature | Importance |
|---|---:|
| `mfg_avg_days_cover` | 27.28% |
| `month` | 24.00% |
| `mfg_units_sold_mean` | 16.43% |
| `mfg_avg_lead_time` | 12.28% |
| `mfg_units_sold_total` | 9.99% |

The first four features account for approximately **80%** of the reported feature importance.

**Business interpretation:** Inventory coverage, seasonality, average sales, and supplier lead time are the most influential features in this trained model. In particular, low days of inventory coverage and longer supplier lead times can be important warning signals for shortage planning.

Feature importance describes how the trained model uses features; it does not prove that a feature causes a shortage.

## Project Files

```text
.
├── demand_shortage_features_with_RF_and_XGBOOST.ipynb
├── demand_shortage_features.csv
├── best_xgb_disruption_model.joblib
└── README.md
```

## Tools & Technologies

- Python
- Pandas and NumPy
- Matplotlib and Seaborn
- Scikit-learn
- XGBoost
- Joblib
- Jupyter Notebook / Google Colab

## Run the Project

1. Clone or download this repository.
2. Install the required libraries:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn xgboost joblib jupyter
```

3. Keep the notebook and CSV file in the same working directory, or update the CSV path in the notebook.
4. Open and run `demand_shortage_features_with_RF_and_XGBOOST.ipynb`.

The notebook currently contains a Google Colab-style CSV path (`/content/demand_shortage_features.csv`). When running locally, change it to:

```python
df = pd.read_csv("demand_shortage_features.csv", na_values=["?"])
```

## Load the Saved Model

The saved file contains the tuned preprocessing-and-classification pipeline.

```python
import joblib
import pandas as pd

model = joblib.load("best_xgb_disruption_model.joblib")

# new_data must contain the same input feature columns
# used during training, excluding the target column.
prediction = model.predict(new_data)
probability = model.predict_proba(new_data)

print("Predicted class:", prediction[0])
print("Urgent-shortage probability:", probability[0][1])
```

Use the same feature definitions and input column structure as the training data. Only load Joblib files from sources you trust.

## Notes & Limitations

- The reported scores are based on the dataset and train-test split used in the notebook; performance on new operational data may differ.
- The tuned XGBoost model achieved the same test accuracy as the baseline models in this experiment, while obtaining a 98.12% cross-validation score.
- The model is a decision-support experiment, not a substitute for inventory-management judgment or operational validation.
- Before real-world deployment, validate the model on newer data and monitor performance over time.
