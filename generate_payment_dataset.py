
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# 1. CONFIGURATION
# ==========================================

rng = np.random.default_rng(42)

NUM_CUSTOMERS = 1000

START_DATE = pd.Timestamp("2023-10-29")
CUTOFF_DATE = pd.Timestamp("2026-10-28")

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. CUSTOMER INFORMATION
# ==========================================

industries = [
    "Technology",
    "Retail",
    "Healthcare",
    "Manufacturing",
    "Construction",
    "Transportation",
    "Professional Services"
]

regions = [
    "Northeast",
    "Southeast",
    "Midwest",
    "Southwest",
    "West"
]

customer_profiles = []

for i in range(1, NUM_CUSTOMERS + 1):

    profile = rng.choice(
        ["Reliable", "Mixed", "Late"],
        p=[0.45, 0.35, 0.20]
    )

    if profile == "Reliable":
        late_probability = 0.12
        discount_probability = 0.70

    elif profile == "Mixed":
        late_probability = 0.40
        discount_probability = 0.40

    else:
        late_probability = 0.72
        discount_probability = 0.15

    customer_profiles.append({

        "customer_id": f"CUST{i:04d}",

        "industry": rng.choice(industries),

        "region": rng.choice(regions),

        "customer_tenure_years": round(
            rng.uniform(0.5, 15), 1
        ),

        "credit_limit": rng.choice([
            10000, 25000, 50000,
            75000, 100000, 150000
        ]),

        "behavior_profile": profile,

        "late_probability": late_probability,

        "discount_probability": discount_probability

    })

customers_df = pd.DataFrame(customer_profiles)

# ==========================================
# 3. PAYMENT TERMS AND DISCOUNTS
# ==========================================

payment_terms = [

    {
        "term_name": "2/10 Net 30",
        "discount_rate": 0.02,
        "discount_days": 10,
        "net_days": 30
    },

    {
        "term_name": "1/10 Net 45",
        "discount_rate": 0.01,
        "discount_days": 10,
        "net_days": 45
    },

    {
        "term_name": "2/15 Net 45",
        "discount_rate": 0.02,
        "discount_days": 15,
        "net_days": 45
    },

    {
        "term_name": "Net 30",
        "discount_rate": 0.00,
        "discount_days": 0,
        "net_days": 30
    },

    {
        "term_name": "Net 45",
        "discount_rate": 0.00,
        "discount_days": 0,
        "net_days": 45
    },

    {
        "term_name": "Net 60",
        "discount_rate": 0.00,
        "discount_days": 0,
        "net_days": 60
    }

]

term_probabilities = [0.15, 0.10, 0.10, 0.35, 0.15, 0.15]

# ==========================================
# 4. GENERATE INVOICES
# ==========================================

invoices = []

invoice_number = 1

total_days = (CUTOFF_DATE - START_DATE).days

for _, customer in customers_df.iterrows():

    number_of_invoices = int(
        rng.integers(30, 43)
    )

    invoice_offsets = np.sort(
        rng.integers(
            0,
            total_days + 1,
            size=number_of_invoices
        )
    )

    for offset in invoice_offsets:

        invoice_date = START_DATE + pd.Timedelta(
            days=int(offset)
        )

        # Generate invoice amount

        invoice_amount = round(
            np.clip(
                rng.lognormal(mean=8.0, sigma=0.8),
                200,
                80000
            ),
            2
        )

        # Select payment terms

        term_index = rng.choice(
            len(payment_terms),
            p=term_probabilities
        )

        term = payment_terms[term_index]

        term_name = term["term_name"]

        discount_rate = term["discount_rate"]

        discount_days = term["discount_days"]

        net_days = term["net_days"]

        due_date = invoice_date + pd.Timedelta(
            days=net_days
        )

        if discount_rate > 0:

            discount_deadline = (
                invoice_date +
                pd.Timedelta(days=discount_days)
            )

            discount_available = True

        else:

            discount_deadline = pd.NaT

            discount_available = False

        # ==================================
        # 5. SIMULATE PAYMENT BEHAVIOR
        # ==================================

        behavior = customer["behavior_profile"]

        late_probability = customer["late_probability"]

        discount_probability = customer["discount_probability"]

        discount_taken = False

        if discount_available:

            if rng.random() < discount_probability:

                discount_taken = True

                payment_date = (
                    invoice_date +
                    pd.Timedelta(
                        days=int(
                            rng.integers(
                                5,
                                discount_days + 1
                            )
                        )
                    )
                )

            else:

                is_late = (
                    rng.random() < late_probability
                )

                if is_late:

                    if behavior == "Reliable":
                        delay = int(rng.integers(1, 8))
                    elif behavior == "Mixed":
                        delay = int(rng.integers(1, 26))
                    else:
                        delay = int(rng.integers(5, 51))

                else:

                    delay = int(rng.integers(-5, 1))

                payment_date = (
                    due_date +
                    pd.Timedelta(days=delay)
                )

        else:

            is_late = (
                rng.random() < late_probability
            )

            if is_late:

                if behavior == "Reliable":
                    delay = int(rng.integers(1, 8))
                elif behavior == "Mixed":
                    delay = int(rng.integers(1, 26))
                else:
                    delay = int(rng.integers(5, 51))

            else:

                delay = int(rng.integers(-5, 1))

            payment_date = (
                due_date +
                pd.Timedelta(days=delay)
            )

        # ==================================
        # 6. OPEN AND PARTIAL INVOICES
        # ==================================

        open_probability = 0.025

        should_remain_open = (
            rng.random() < open_probability
            or payment_date > CUTOFF_DATE
        )

        amount_paid = 0.0

        discount_amount = 0.0

        actual_days_to_pay = np.nan

        actual_days_late = np.nan

        last_payment_date = pd.NaT

        if should_remain_open:

            # Some unpaid invoices receive partial payments

            if rng.random() < 0.35:

                payment_fraction = rng.uniform(
                    0.20, 0.80
                )

                amount_paid = round(
                    invoice_amount * payment_fraction,
                    2
                )

                last_payment_date = (
                    min(
                        CUTOFF_DATE,
                        invoice_date +
                        pd.Timedelta(
                            days=int(
                                rng.integers(
                                    5,
                                    max(
                                        6,
                                        (CUTOFF_DATE - invoice_date).days + 1
                                    )
                                )
                            )
                        )
                    )
                )

                payment_status = "Partially Paid"

            else:

                payment_status = "Overdue" if (
                    due_date < CUTOFF_DATE
                ) else "Open"

        else:

            # Full invoice payment

            last_payment_date = payment_date

            actual_days_to_pay = (
                payment_date - invoice_date
            ).days

            actual_days_late = (
                payment_date - due_date
            ).days

            if discount_taken:

                discount_amount = round(
                    invoice_amount * discount_rate,
                    2
                )

            amount_paid = round(
                invoice_amount - discount_amount,
                2
            )

            payment_status = "Paid"

        # ==================================
        # 7. CALCULATE OUTSTANDING BALANCE
        # ==================================

        outstanding_balance = round(
            invoice_amount -
            discount_amount -
            amount_paid,
            2
        )

        # ==================================
        # 8. SAVE INVOICE RECORD
        # ==================================

        invoices.append({

            "invoice_id": f"INV{invoice_number:07d}",

            "customer_id": customer["customer_id"],

            "invoice_date": invoice_date,

            "due_date": due_date,

            "invoice_amount": invoice_amount,

            "payment_terms": term_name,

            "payment_terms_days": net_days,

            "discount_available": discount_available,

            "discount_rate": discount_rate,

            "discount_days": discount_days,

            "discount_deadline": discount_deadline,

            "discount_taken": discount_taken
            if payment_status == "Paid" else False,

            "discount_amount": discount_amount,

            "amount_paid": amount_paid,

            "outstanding_balance": outstanding_balance,

            "payment_date": last_payment_date,

            "payment_status": payment_status,

            "actual_days_to_pay": actual_days_to_pay,

            "days_late": actual_days_late,

            "industry": customer["industry"],

            "region": customer["region"],

            "customer_tenure_years":
                customer["customer_tenure_years"],

            "credit_limit": customer["credit_limit"],

            "behavior_profile": customer["behavior_profile"]

        })

        invoice_number += 1

# ==========================================
# 9. CREATE DATAFRAMES
# ==========================================

invoices_df = pd.DataFrame(invoices)

# ==========================================
# 10. CREATE PAYMENT CLASSIFICATION TARGET
# ==========================================

invoices_df["paid_late"] = np.where(
    invoices_df["payment_status"] == "Paid",
    (invoices_df["days_late"] > 0).astype(int),
    np.nan
)

# ==========================================
# 11. SAVE DATASETS
# ==========================================

invoice_path = (
    OUTPUT_DIR / "customer_payment_invoices.csv"
)

customer_path = (
    OUTPUT_DIR / "customer_master.csv"
)

invoices_df.to_csv(
    invoice_path,
    index=False
)

customers_df.to_csv(
    customer_path,
    index=False
)

# ==========================================
# 12. DISPLAY DATASET SUMMARY
# ==========================================

print("\n===================================")
print("CUSTOMER PAYMENT DATASET GENERATED")
print("===================================")

print(
    "Total Customers:",
    customers_df["customer_id"].nunique()
)

print(
    "Total Invoices:",
    len(invoices_df)
)

print(
    "Date Range:",
    invoices_df["invoice_date"].min(),
    "to",
    invoices_df["invoice_date"].max()
)

print("\nPAYMENT STATUS DISTRIBUTION")

print(
    invoices_df["payment_status"].value_counts()
)

print("\nPAYMENT TERMS DISTRIBUTION")

print(
    invoices_df["payment_terms"].value_counts()
)

print("\nDISCOUNT ANALYSIS")

print(
    "Invoices with Discount:",
    invoices_df["discount_available"].sum()
)

print(
    "Discounts Actually Taken:",
    invoices_df["discount_taken"].sum()
)

print(
    "Total Discount Given: $",
    round(invoices_df["discount_amount"].sum(), 2)
)

print(
    "Total Outstanding: $",
    round(invoices_df["outstanding_balance"].sum(), 2)
)

print("\nFILES CREATED")

print(invoice_path)
print(customer_path)

print("\nFIRST FIVE INVOICES")

print(invoices_df.head())
