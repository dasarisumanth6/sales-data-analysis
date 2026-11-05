import csv
import pandas as pd
import numpy as np
import matplotlib

# Configure Matplotlib to use a desktop window backend.
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from collections import defaultdict

# ==========================================
# 1. READ AND VALIDATE SALES DATA
# ==========================================

df = pd.read_csv("sales_data.csv")

required_columns = ["product", "quantity", "price", "date"]

if not all(column in df.columns for column in required_columns):
    raise ValueError(
        "sales_data.csv must contain: product, quantity, price, date"
    )

df["product"] = df["product"].fillna("").astype(str).str.strip()
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
df["price"] = pd.to_numeric(df["price"], errors="coerce")

df["date"] = pd.to_datetime(
    df["date"], format="%Y-%m-%d", errors="coerce"
)

valid_rows = (
    df["product"].ne("")
    & df["quantity"].gt(0)
    & df["quantity"].notna()
    & df["quantity"].mod(1).eq(0)
    & df["price"].ge(0)
    & df["price"].notna()
    & df["date"].notna()
)

invalid_df = df.loc[~valid_rows].copy()
df = df.loc[valid_rows].copy()

if not invalid_df.empty:
    print("\nINVALID SALES RECORDS FOUND:")
    print(invalid_df[required_columns])

df["quantity"] = df["quantity"].astype(int)

print("\nSALES DATA TABLE (VALID RECORDS ONLY)")
print(df[required_columns])

# ==========================================
# 2. CALCULATE REVENUE
# ==========================================

df["revenue"] = df["quantity"] * df["price"]

print("\nSALES DATA WITH REVENUE")
print(df[required_columns + ["revenue"]])

# ==========================================
# 3. PRODUCT-WISE REVENUE ANALYSIS
# ==========================================

product_revenue = df.groupby("product")["revenue"].sum()

print("\nPRODUCT-WISE TOTAL REVENUE")
print(product_revenue)

if not product_revenue.empty:
    highest_revenue_product = product_revenue.idxmax()
    highest_product_revenue = product_revenue.max()

    print("\nHIGHEST REVENUE PRODUCT")
    print("Product:", highest_revenue_product)
    print("Total Revenue: ₹", highest_product_revenue)
else:
    print("\nNo valid product sales available.")

# ==========================================
# 4. MONTHLY REVENUE ANALYSIS
# ==========================================

df["month"] = df["date"].dt.to_period("M")
monthly_sales_pandas = df.groupby("month")["revenue"].sum()

print("\nMONTHLY REVENUE")
print(monthly_sales_pandas)

# ==========================================
# 5. TOTAL AND AVERAGE REVENUE
# ==========================================

total_sales_pandas = df["revenue"].sum()
average_revenue = (
    float(np.mean(df["revenue"])) if not df.empty else 0
)

print("\nTOTAL REVENUE: ₹", round(total_sales_pandas, 2))
print("AVERAGE REVENUE PER SALE: ₹", round(average_revenue, 2))

# ==========================================
# 6. FINAL SALES SUMMARY
# ==========================================

print("\n========== FINAL SALES SUMMARY ==========")
print("Total Revenue: ₹", round(total_sales_pandas, 2))
print("Average Revenue per Sale: ₹", round(average_revenue, 2))
print("Total Quantity Sold:", df["quantity"].sum())
print("Number of Valid Sales Records:", len(df))
print("Number of Invalid Records:", len(invalid_df))
print("=========================================")

# ==========================================
# 7. PYTHON SALES ANALYSIS
# ==========================================

print("\n============================")
print("     SALES DATA ANALYSIS")
print("============================")

monthly_revenue = defaultdict(float)
product_quantity = defaultdict(int)

total_revenue = 0
total_quantity = 0
highest_single_sale_revenue = -1
highest_single_sale_product = ""

for _, row in df.iterrows():
    product = row["product"]
    quantity = int(row["quantity"])
    price = float(row["price"])
    date = row["date"]

    revenue = quantity * price
    month = date.strftime("%Y-%m")

    product_quantity[product] += quantity
    monthly_revenue[month] += revenue

    if revenue > highest_single_sale_revenue:
        highest_single_sale_revenue = revenue
        highest_single_sale_product = product

    total_revenue += revenue
    total_quantity += quantity

    print(product, "Revenue: ₹", revenue)

print("----------------------------")
print("Total Revenue: ₹", total_revenue)
print("Total Quantity Sold:", total_quantity)
print("----------------------------")

if highest_single_sale_product:
    print(
        "Product with Highest Single-Sale Revenue:",
        highest_single_sale_product
    )
    print("Highest Single-Sale Revenue: ₹", highest_single_sale_revenue)

if product_quantity:
    highest_sold_quantity = max(product_quantity.values())

    print("\nBest-Selling Products:")

    for product, quantity in sorted(product_quantity.items()):
        if quantity == highest_sold_quantity:
            print(product, ":", quantity, "units")

print("\nPRODUCT-WISE QUANTITY SOLD")

for product, quantity in sorted(product_quantity.items()):
    print(product, ":", quantity)

print("\nMONTHLY SALES ANALYSIS")

for month, revenue in sorted(monthly_revenue.items()):
    print(month, "Revenue: ₹", revenue)

# ==========================================
# 8. SAVE INVALID RECORDS TO CSV
# ==========================================

with open("validation_errors.csv", "w", newline="", encoding="utf-8") as error_file:
    fieldnames = ["product", "quantity", "price", "date"]
    writer = csv.DictWriter(error_file, fieldnames=fieldnames)
    writer.writeheader()

    if not invalid_df.empty:
        error_records = invalid_df[required_columns].copy()

        error_records["date"] = error_records["date"].apply(
            lambda value: value.strftime("%Y-%m-%d")
            if pd.notna(value) else ""
        )

        error_records["quantity"] = error_records["quantity"].apply(
            lambda value: value if pd.notna(value) else ""
        )

        error_records["price"] = error_records["price"].apply(
            lambda value: value if pd.notna(value) else ""
        )

        writer.writerows(error_records.to_dict("records"))

print("\nValidation error report saved to validation_errors.csv")

# ==========================================
# 9. PRODUCT REVENUE CHART
# ==========================================

if not product_revenue.empty:
    print("\nOpening product revenue chart...")

    fig1, ax1 = plt.subplots(figsize=(9, 5))

    bars = ax1.bar(
        product_revenue.index.astype(str),
        product_revenue.values
    )

    ax1.set_title("Total Revenue by Product")
    ax1.set_xlabel("Products")
    ax1.set_ylabel("Revenue (Rs.)")
    ax1.bar_label(bars, fmt="%.0f")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    fig1.tight_layout()

    # Save a copy of the chart as an image.
    fig1.savefig("product_revenue_chart.png", dpi=150)

else:
    print("\nNo valid sales data available for the product chart.")

# ==========================================
# 10. MONTHLY REVENUE CHART
# ==========================================

if monthly_revenue:
    print("Opening monthly revenue chart...")

    months = sorted(monthly_revenue.keys())
    monthly_values = [monthly_revenue[month] for month in months]

    fig2, ax2 = plt.subplots(figsize=(9, 5))

    bars = ax2.bar(months, monthly_values)

    ax2.set_title("Monthly Sales Revenue")
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Revenue (Rs.)")
    ax2.bar_label(bars, fmt="%.0f")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    fig2.tight_layout()

    # Save a copy of the chart as an image.
    fig2.savefig("monthly_revenue_chart.png", dpi=150)

else:
    print("No monthly sales data available.")

# ==========================================
# 11. DISPLAY ALL CHARTS
# ==========================================

if product_revenue.empty and not monthly_revenue:
    print("\nNo charts to display.")
else:
    print("\nDisplaying charts. Close the chart windows to finish.")
    plt.show(block=True)

print("\nSales Data Analysis completed successfully!")