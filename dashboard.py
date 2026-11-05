import streamlit as st
import pandas as pd

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# 2. PROFESSIONAL DESIGN
# ==================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 36px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        color: #64748b;
        font-size: 16px;
        margin-top: 5px;
        margin-bottom: 25px;
    }

    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<p class="main-title">📊 Sales Analytics Dashboard</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">Monitor revenue, analyze products, '
    'and understand sales performance.</p>',
    unsafe_allow_html=True
)

# ==================================================
# 3. LOAD AND VALIDATE DATA
# ==================================================

@st.cache_data
def load_data():
    df = pd.read_csv("sales_data.csv")

    required_columns = ["product", "quantity", "price", "date"]

    if not all(column in df.columns for column in required_columns):
        raise ValueError(
            "CSV must contain product, quantity, price, and date columns."
        )

    df["product"] = df["product"].fillna("").astype(str).str.strip()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    df["date"] = pd.to_datetime(
        df["date"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    valid = (
        df["product"].ne("")
        & df["quantity"].notna()
        & df["quantity"].gt(0)
        & df["quantity"].mod(1).eq(0)
        & df["price"].notna()
        & df["price"].ge(0)
        & df["date"].notna()
    )

    invalid_df = df.loc[~valid].copy()
    df = df.loc[valid].copy()

    df["quantity"] = df["quantity"].astype(int)
    df["revenue"] = df["quantity"] * df["price"]

    return df, invalid_df


try:
    df, invalid_df = load_data()

except (
    FileNotFoundError,
    ValueError,
    pd.errors.ParserError,
    UnicodeDecodeError
) as error:
    st.error(f"Unable to load sales data: {error}")
    st.stop()

if df.empty:
    st.warning("No valid sales records are available.")
    st.stop()

# ==================================================
# 4. SIDEBAR FILTERS
# ==================================================

st.sidebar.title("🔎 Dashboard Filters")
st.sidebar.caption("Customize your sales analysis.")

minimum_date = df["date"].min().date()
maximum_date = df["date"].max().date()

selected_dates = st.sidebar.date_input(
    "📅 Select date range",
    value=(minimum_date, maximum_date),
    min_value=minimum_date,
    max_value=maximum_date
)

all_products = sorted(df["product"].unique().tolist())

selected_products = st.sidebar.multiselect(
    "🛍️ Select products",
    options=all_products,
    default=all_products
)

if st.sidebar.button("🔄 Reset filters"):
    st.session_state.clear()
    st.rerun()

# ==================================================
# 5. APPLY FILTERS
# ==================================================

filtered_df = df.copy()

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        filtered_df["date"].dt.date.between(start_date, end_date)
    ]

elif isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 1:
    selected_date = selected_dates[0]

    filtered_df = filtered_df[
        filtered_df["date"].dt.date == selected_date
    ]

filtered_df = filtered_df[
    filtered_df["product"].isin(selected_products)
]

st.caption(
    f"Showing {len(filtered_df):,} of {len(df):,} valid sales records"
)

# ==================================================
# 6. DISPLAY DASHBOARD
# ==================================================

if filtered_df.empty:
    st.warning(
        "No sales records match your filters. "
        "Please choose another date range or product."
    )

else:
    # ----------------------------------------------
    # KPI CARDS
    # ----------------------------------------------

    total_revenue = filtered_df["revenue"].sum()
    total_quantity = filtered_df["quantity"].sum()
    total_records = len(filtered_df)
    average_revenue = filtered_df["revenue"].mean()

    st.subheader("📌 Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💰 Total Revenue",
        f"₹{total_revenue:,.2f}"
    )

    col2.metric(
        "📦 Units Sold",
        f"{total_quantity:,}"
    )

    col3.metric(
        "🧾 Valid Sales",
        f"{total_records:,}"
    )

    col4.metric(
        "📊 Average Sale",
        f"₹{average_revenue:,.2f}"
    )

    st.divider()

    # ----------------------------------------------
    # PRODUCT PERFORMANCE
    # ----------------------------------------------

    st.subheader("🏆 Product Performance")

    product_revenue = (
        filtered_df.groupby("product")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    product_quantity = (
        filtered_df.groupby("product")["quantity"]
        .sum()
        .sort_values(ascending=False)
    )

    left, right = st.columns(2)

    with left:
        st.write("**Revenue by Product**")
        st.bar_chart(product_revenue)

    with right:
        st.write("**Quantity Sold by Product**")
        st.bar_chart(product_quantity)

    top_revenue_product = product_revenue.idxmax()

    highest_quantity = product_quantity.max()

    best_selling_products = product_quantity[
        product_quantity == highest_quantity
    ].index.tolist()

    insight1, insight2 = st.columns(2)

    with insight1:
        st.info(
            f"💰 Highest revenue product: {top_revenue_product}"
        )

    with insight2:
        st.info(
            "📦 Best-selling product(s): "
            + ", ".join(best_selling_products)
        )

    st.divider()

    # ----------------------------------------------
    # MONTHLY REVENUE
    # ----------------------------------------------

    st.subheader("📅 Monthly Revenue")

    monthly_data = filtered_df.copy()

    monthly_data["month"] = (
        monthly_data["date"].dt.to_period("M").astype(str)
    )

    monthly_revenue = monthly_data.groupby("month")["revenue"].sum()

    if not monthly_revenue.empty:
        st.bar_chart(monthly_revenue)

        best_month = monthly_revenue.idxmax()

        st.success(
            f"📈 Highest revenue month: {best_month} "
            f"(₹{monthly_revenue[best_month]:,.2f})"
        )
    else:
        st.info("No monthly revenue data is available.")

    st.divider()

    # ----------------------------------------------
    # SALES TABLE AND CSV DOWNLOAD
    # ----------------------------------------------

    st.subheader("📋 Sales Records")

    display_df = filtered_df.copy()
    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True
    )

    csv_data = display_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Sales CSV",
        data=csv_data,
        file_name="filtered_sales_data.csv",
        mime="text/csv"
    )

# ==================================================
# 7. DATA VALIDATION REPORT
# ==================================================

st.divider()
st.subheader("⚠️ Data Quality Report")

if invalid_df.empty:
    st.success("All source records passed validation.")

else:
    st.warning(
        f"{len(invalid_df)} invalid record(s) found in the source CSV."
    )

    error_display = invalid_df.copy()
    error_display["date"] = error_display["date"].astype(str)

    st.dataframe(
        error_display,
        width="stretch",
        hide_index=True
    )

    invalid_csv = error_display.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Invalid Records",
        data=invalid_csv,
        file_name="validation_errors.csv",
        mime="text/csv"
    )

# ==================================================
# 8. FOOTER
# ==================================================

st.divider()

st.caption(
    "Sales Analytics Dashboard | Built with Python, Pandas and Streamlit"
)