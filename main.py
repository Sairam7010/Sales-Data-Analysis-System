import pandas as pd

# Load sales dataset
df = pd.read_csv("sales_data.csv")

# Calculate revenue
df["Revenue"] = df["Quantity"] * df["UnitPrice"]

print("\n===== SALES DATASET =====")
print(df.to_string(index=False))

print("\n===== SALES SUMMARY =====")
print("Total Orders:", len(df))
print("Total Quantity Sold:", df["Quantity"].sum())
print("Total Revenue: Rs.", df["Revenue"].sum())

print("\n===== PRODUCT-WISE REVENUE =====")
product_sales = df.groupby("Product")["Revenue"].sum()

print(product_sales.sort_values(ascending=False))


# Monthly Sales Analysis

print("\n===== MONTHLY SALES ANALYSIS =====")

df["OrderDate"] = pd.to_datetime(df["OrderDate"])

df["Month"] = df["OrderDate"].dt.strftime("%B")

monthly_sales = df.groupby("Month")["Revenue"].sum()

print(monthly_sales)

print("\n===== HIGHEST SALES MONTH =====")

best_month = monthly_sales.idxmax()
best_revenue = monthly_sales.max()

print("Best Month:", best_month)
print("Revenue: Rs.", best_revenue)


import matplotlib.pyplot as plt

# Monthly Sales Bar Chart
monthly_sales = df.groupby(
    df["OrderDate"].dt.to_period("M")
)["Revenue"].sum()

plt.figure(figsize=(10, 5))

monthly_sales.index = monthly_sales.index.astype(str)

plt.bar(monthly_sales.index, monthly_sales.values)

plt.title("Monthly Sales Revenue")
plt.xlabel("Month")
plt.ylabel("Revenue (Rs.)")

plt.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("output/monthly_sales.png")
plt.show()


# Product-wise Revenue Chart

product_sales = df.groupby("Product")["Revenue"].sum()

plt.figure(figsize=(10, 5))

plt.bar(product_sales.index, product_sales.values)

plt.title("Product-wise Revenue Analysis")
plt.xlabel("Products")
plt.ylabel("Revenue (Rs.)")

plt.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("output/product_sales.png")
plt.show()


# Region-wise Sales Analysis

print("\n===== REGION-WISE SALES =====")

region_sales = df.groupby("Region")["Revenue"].sum()

print(region_sales.sort_values(ascending=False))

print("\nTop Performing Region:")
print(region_sales.idxmax())

print("Revenue: Rs.", region_sales.max())


# Category-wise Sales Analysis

print("\n===== CATEGORY-WISE SALES =====")

category_sales = df.groupby("Category")["Revenue"].sum()

print(category_sales.sort_values(ascending=False))

print("\nTop Performing Category:")
print(category_sales.idxmax())

print("Revenue: Rs.", category_sales.max())


plt.figure(figsize=(8, 5))

plt.bar(region_sales.index, region_sales.values)

plt.title("Region-wise Sales Revenue")
plt.xlabel("Region")
plt.ylabel("Revenue (Rs.)")

plt.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("output/region_sales.png")
plt.show()


plt.figure(figsize=(7, 7))

plt.pie(
    category_sales.values,
    labels=category_sales.index,
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Category-wise Revenue Distribution")

plt.tight_layout()
plt.savefig("output/category_sales.png")
plt.show()


import os
import matplotlib.pyplot as plt

# Create output folder if not exists
os.makedirs("output", exist_ok=True)

# Prepare analysis data
df["OrderDate"] = pd.to_datetime(df["OrderDate"])

total_revenue = df["Revenue"].sum()
total_orders = len(df)
total_quantity = df["Quantity"].sum()
average_order_value = total_revenue / total_orders

monthly_sales = df.groupby(
    df["OrderDate"].dt.to_period("M")
)["Revenue"].sum()

product_sales = df.groupby("Product")["Revenue"].sum()
region_sales = df.groupby("Region")["Revenue"].sum()
category_sales = df.groupby("Category")["Revenue"].sum()

best_product = product_sales.idxmax()
best_region = region_sales.idxmax()

# Create dashboard
fig, axes = plt.subplots(2, 2, figsize=(14, 9))

fig.suptitle(
    "SALES ANALYTICS DASHBOARD",
    fontsize=20,
    fontweight="bold"
)

# KPI summary
fig.text(
    0.12, 0.91,
    f"Revenue: Rs. {total_revenue:,.0f}",
    fontsize=12
)

fig.text(
    0.36, 0.91,
    f"Orders: {total_orders}",
    fontsize=12
)

fig.text(
    0.56, 0.91,
    f"Quantity: {total_quantity}",
    fontsize=12
)

fig.text(
    0.75, 0.91,
    f"Avg Order: Rs. {average_order_value:,.0f}",
    fontsize=12
)

# 1. Monthly sales trend
monthly_labels = monthly_sales.index.astype(str)

axes[0, 0].plot(
    monthly_labels,
    monthly_sales.values,
    marker="o"
)

axes[0, 0].set_title("Monthly Sales Trend")
axes[0, 0].set_xlabel("Month")
axes[0, 0].set_ylabel("Revenue (Rs.)")
axes[0, 0].grid(True, alpha=0.3)

# 2. Product-wise revenue
axes[0, 1].bar(
    product_sales.index,
    product_sales.values
)

axes[0, 1].set_title("Product-wise Revenue")
axes[0, 1].set_ylabel("Revenue (Rs.)")

# 3. Region-wise revenue
axes[1, 0].bar(
    region_sales.index,
    region_sales.values
)

axes[1, 0].set_title("Region-wise Revenue")
axes[1, 0].set_ylabel("Revenue (Rs.)")

# 4. Category-wise revenue
axes[1, 1].pie(
    category_sales.values,
    labels=category_sales.index,
    autopct="%1.1f%%",
    startangle=90
)

axes[1, 1].set_title("Category-wise Revenue")

# Best performers
fig.text(
    0.5, 0.025,
    f"Top Product: {best_product} | "
    f"Top Region: {best_region}",
    ha="center",
    fontsize=12,
    fontweight="bold"
)

plt.tight_layout(rect=[0, 0.06, 1, 0.88])

# Save dashboard
plt.savefig(
    "output/sales_dashboard.png",
    dpi=150,
    bbox_inches="tight"
)

plt.show()

print("\nDashboard created successfully!")
print("File: output/sales_dashboard.png")
