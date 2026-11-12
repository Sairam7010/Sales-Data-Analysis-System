
import streamlit as st
import pandas as pd
from database import (
    get_sales_data,
    add_sale,
    update_sale,
    delete_sale
)

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Dashboard Header
st.title("📊 Sales Data Analysis Dashboard")

st.markdown(
    "Analyze sales performance, revenue, products and regions "
    "using interactive data visualization."
)

st.divider()

# Load PostgreSQL data
try:
    df = get_sales_data()

except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

if df.empty:
    st.warning("No sales records found.")
    st.stop()



# SIDEBAR FILTERS


st.sidebar.header("Sales Filters")

# 1. Product Search
search_product = st.sidebar.text_input(
    "Search Product",
    placeholder="Enter product name..."
)

# 2. Region Filter
regions_list = sorted(df["region"].dropna().unique())

regions = st.sidebar.multiselect(
    "Select Region",
    options=regions_list,
    default=regions_list,
    key="region_filter"
)

# 3. Category Filter
categories_list = sorted(df["category"].dropna().unique())

categories = st.sidebar.multiselect(
    "Select Category",
    options=categories_list,
    default=categories_list,
    key="category_filter"
)

# 4. Date Range Filter
df["order_date"] = pd.to_datetime(df["order_date"])

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(
        df["order_date"].min().date(),
        df["order_date"].max().date()
    ),
    key="date_filter"
)

# ==================================
# APPLY FILTERS
# ==================================

# Apply Region and Category Filters
filtered_df = df[
    (df["region"].isin(regions)) &
    (df["category"].isin(categories))
].copy()

# Apply Product Search
if search_product.strip():
    filtered_df = filtered_df[
        filtered_df["product"].str.contains(
            search_product.strip(),
            case=False,
            na=False
        )
    ]

# Apply Date Range Filter
if len(date_range) == 2:
    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["order_date"].dt.date >= start_date) &
        (filtered_df["order_date"].dt.date <= end_date)
    ]

# Check empty results
if filtered_df.empty:
    st.warning("No matching sales records found.")
    st.stop()



# DYNAMIC KPI CARDS


total_revenue = filtered_df["revenue"].sum()

total_orders = len(filtered_df)

total_quantity = filtered_df["quantity"].sum()

average_order_value = (
    total_revenue / total_orders
    if total_orders > 0
    else 0
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Revenue",
        f"₹{total_revenue:,.2f}"
    )

with col2:
    st.metric(
        "Total Orders",
        f"{total_orders:,}"
    )

with col3:
    st.metric(
        "Total Quantity",
        f"{total_quantity:,}"
    )

with col4:
    st.metric(
        "Average Order Value",
        f"₹{average_order_value:,.2f}"
    )

# Monthly sales analysis
st.subheader("📅 Monthly Sales Performance")

filtered_df["order_date"] = pd.to_datetime(
    filtered_df["order_date"]
)

monthly_sales = (
    filtered_df
    .groupby(filtered_df["order_date"].dt.to_period("M"))["revenue"]
    .sum()
)

monthly_sales.index = monthly_sales.index.astype(str)

st.line_chart(monthly_sales)

# Product and region analysis
col5, col6 = st.columns(2)

with col5:
    st.subheader("📦 Product-wise Sales Analysis")
    product_sales = filtered_df.groupby("product")["revenue"].sum()
    st.bar_chart(product_sales)

with col6:
    st.subheader("🌍 Region-wise Sales Analysis")
    region_sales = filtered_df.groupby("region")["revenue"].sum()
    st.bar_chart(region_sales)

# Category analysis
st.subheader("📈 Category-wise Sales Analysis")

category_sales = filtered_df.groupby("category")["revenue"].sum()
st.bar_chart(category_sales)



# Add New Sale
st.divider()
st.subheader("➕ Add New Sale")

with st.form("add_sale_form", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        order_date = st.date_input("Order Date")

        product = st.selectbox(
            "Product",
            ["Laptop", "Mouse", "Keyboard", "Monitor", "Other"]
        )

        category = st.selectbox(
            "Category",
            ["Electronics", "Accessories", "Other"]
        )

    with col2:
        region = st.selectbox(
            "Region",
            ["South", "North", "East", "West"]
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1,
            step=1
        )

        unit_price = st.number_input(
            "Unit Price (Rs.)",
            min_value=0.0,
            value=1000.0,
            step=100.0
        )

    submitted = st.form_submit_button(
        "Add Sale",
        use_container_width=True
    )

    if submitted:
        if not product.strip():
            st.error("Product name is required.")

        elif not category.strip():
            st.error("Category is required.")

        elif not region.strip():
            st.error("Region is required.")

        elif quantity <= 0:
            st.error("Quantity must be greater than zero.")

        elif unit_price < 0:
            st.error("Unit price cannot be negative.")

        else:
            try:
                new_id = add_sale(
                    order_date,
                    product.strip(),
                    category.strip(),
                    region.strip(),
                    quantity,
                    unit_price
                )

                st.success(
                    f"Sale added successfully! Order ID: {new_id}"
                )

                st.rerun()

            except Exception as e:
                st.error(f"Unable to add sale: {e}")


# Update Existing Sale
st.divider()
st.subheader("✏️ Update Existing Sale")

# Select existing order
order_options = filtered_df["order_id"].tolist()

if order_options:

    selected_id = st.selectbox(
        "Select Order ID to Update",
        order_options,
        key="update_order_id"
    )

    selected_sale = df[
        df["order_id"] == selected_id
    ].iloc[0]

    with st.form("update_sale_form"):

        col1, col2 = st.columns(2)

        with col1:
            edit_date = st.date_input(
                "Order Date",
                value=pd.to_datetime(
                    selected_sale["order_date"]
                ).date()
            )

            edit_product = st.text_input(
                "Product",
                value=str(selected_sale["product"])
            )

            edit_category = st.text_input(
                "Category",
                value=str(selected_sale["category"])
            )

        with col2:
            edit_region = st.text_input(
                "Region",
                value=str(selected_sale["region"])
            )

            edit_quantity = st.number_input(
                "Quantity",
                min_value=1,
                value=int(selected_sale["quantity"])
            )

            edit_price = st.number_input(
                "Unit Price",
                min_value=0.0,
                value=float(selected_sale["unit_price"])
            )

        update_button = st.form_submit_button(
            "Update Sale",
            use_container_width=True
        )

        if update_button:

            try:
                updated_id = update_sale(
                    selected_id,
                    edit_date,
                    edit_product.strip(),
                    edit_category.strip(),
                    edit_region.strip(),
                    edit_quantity,
                    edit_price
                )

                if updated_id is not None:
                    st.success(
                        f"Order {updated_id} updated successfully!"
                    )
                    st.rerun()
                else:
                    st.warning("Order ID not found.")

            except Exception as e:
                st.error(f"Update failed: {e}")

else:
    st.info("No sales records available to update.")


# Delete Existing Sale
st.divider()
st.subheader("🗑️ Delete Existing Sale")

delete_options = filtered_df["order_id"].tolist()

if delete_options:

    delete_id = st.selectbox(
        "Select Order ID to Delete",
        delete_options,
        key="delete_order_id"
    )

    selected_delete = df[
        df["order_id"] == delete_id
    ].iloc[0]

    st.write("Selected Sale Details")

    st.write(f"Product: {selected_delete['product']}")
    st.write(f"Region: {selected_delete['region']}")
    st.write(f"Quantity: {selected_delete['quantity']}")
    st.write(f"Revenue: ₹{selected_delete['revenue']:,.2f}")

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this sale",
        key="confirm_delete"
    )

    if st.button(
        "Delete Sale",
        disabled=not confirm_delete,
        type="primary",
        key="delete_sale_button"
    ):

        try:
            deleted_id = delete_sale(delete_id)

            if deleted_id is not None:
                st.success(
                    f"Order {deleted_id} deleted successfully!"
                )
                st.rerun()
            else:
                st.warning("Order ID not found.")

        except Exception as e:
            st.error(f"Delete failed: {e}")

else:
    st.info("No sales records available to delete.")


# Sales records
st.subheader("Sales Records")
st.dataframe(filtered_df, use_container_width=True)

# Download report
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Sales Report",
    data=csv_data,
    file_name="sales_report.csv",
    mime="text/csv",
    key="download_sales_report"
)

st.success("PostgreSQL data loaded successfully!")
