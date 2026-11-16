# Customer Payment Prediction & Financial Risk Analytics

## Project Overview

This project uses machine learning to predict whether a customer invoice will be paid late. It analyzes historical payment behavior, invoice characteristics, payment terms, discounts, and customer information to identify potential payment risks.

The goal is to help finance teams prioritize collection efforts, anticipate cash flow, and make better working-capital decisions.

**Dataset:** This project uses synthetic data generated for educational and portfolio purposes. It does not contain real customer or company financial information.

## Business Problem

Late customer payments create cash-flow uncertainty and increase the time and effort required to collect outstanding invoices.

This project explores how predictive analytics can help finance teams:

- Identify invoices with a higher risk of late payment
- Prioritize customers for collection follow-up
- Improve cash collection forecasting
- Understand factors associated with late payments
- Evaluate payment terms and early-payment discounts

## Dataset

The project uses two synthetic datasets:

- `customer_payment_invoices.csv` — invoice-level payment history and financial information
- `customer_master.csv` — customer-level information

The invoice dataset contains approximately **36,000 invoice records across 1,000 customers**.

Key variables include:

- Invoice amount
- Payment terms
- Early-payment discount information
- Customer industry and region
- Customer tenure and credit limit
- Historical late-payment rate
- Historical average days to pay
- Payment outcomes

## Methodology

### 1. Exploratory Data Analysis

Analyzed invoice amounts, collections, outstanding balances, late-payment patterns, industry trends, customer behavior, and discount usage.

### 2. Data Preparation and Feature Engineering

Created time-based invoice features, invoice-to-credit-limit ratios, and historical customer payment behavior features.

Historical features were calculated using only payment information available before each invoice date to reduce data leakage.

Unpaid invoices were excluded from supervised classification because their final payment outcomes were not yet known.

### 3. Machine Learning

Built and evaluated three classification models:

- Random Forest
- XGBoost
- Tuned XGBoost

Used a chronological train/test split to evaluate performance on later invoices. Preprocessing was performed within a machine-learning pipeline.

## Model Performance

| Model | Accuracy | ROC-AUC |
|---|---:|---:|
| Random Forest | 73.55% | 0.7965 |
| XGBoost | 78.19% | 0.7969 |
| **Tuned XGBoost** | **78.50%** | **0.7998** |

The tuned XGBoost model achieved the strongest overall results on the held-out test set.

ROC-AUC measures how well a model distinguishes between invoices paid late and those paid on time. It is not the same as accuracy.

## Key Findings

The most influential model features included:

1. Historical late-payment rate
2. Historical average days to pay
3. Discount rate
4. Number of previously paid invoices
5. Invoice year
6. Discount days

Historical payment behavior was especially important to the model's predictions.

Feature importance indicates which variables the model relies on most. It does not establish that those variables cause late payments.

## Business Value

A predictive payment-risk model could help finance teams focus collection efforts on invoices with higher predicted late-payment risk.

For illustration, if a business invoices $2 million per month and 30% of that amount is exposed to late payment, a 15% reduction in that late-payment exposure would represent **$90,000 in monthly cash-flow acceleration**, or $1.08 million annualized.

This is an illustrative scenario, not a measured result or guaranteed financial benefit from this model.

## Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- XGBoost
- Jupyter Notebook

## Project Structure

```text
customer-payment-prediction/
├── data/
│   └── raw/
│       ├── customer_master.csv
│       └── customer_payment_invoices.csv
├── notebooks/
│   └── 02_exploratory_analysis.ipynb
├── generate_payment_dataset.py
├── requirements.txt
├── README.md
└── .gitignore
```

## How to Run

1. Clone the repository:

   ```bash
   git clone https://github.com/amanrunwal/customer-payment-prediction.git
   cd customer-payment-prediction
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Open Jupyter Notebook:

   ```bash
   jupyter notebook
   ```

5. Open `notebooks/02_exploratory_analysis.ipynb` and run the analysis.

To regenerate the synthetic datasets:

```bash
python generate_payment_dataset.py
```

## Limitations and Future Improvements

- The project uses synthetic rather than real company data.
- Model performance should be validated on real historical invoice data before business use.
- The classification model only includes invoices with known payment outcomes.
- Future improvements could include SHAP explanations, probability calibration, cash collection forecasting, and a Streamlit dashboard.

## Disclaimer

This project is for educational and portfolio purposes. Model predictions should support, not replace, business judgment.
