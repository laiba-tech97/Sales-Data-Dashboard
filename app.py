import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE SETTINGS
st.set_page_config(
    page_title="Sales Data Analysis",
    page_icon="📊",
    layout="wide"
)

# TITLE
st.title("📊 Sales Data Analysis Dashboard")
st.markdown("### E-commerce Sales Performance | 2019")

# LOAD DATA
df = pd.read_csv("Sales Data - Sales Data.csv")

# DATA CLEANING
df = df.drop(columns="Unnamed: 0", errors="ignore")
df = df.dropna().drop_duplicates()

df["Order Date"] = pd.to_datetime(
    df["Order Date"], errors="coerce"
)
df = df.dropna(subset=["Order Date"])

df = df[df["Order Date"].dt.year == 2019].copy()

df["Sales"] = df["Quantity Ordered"] * df["Price Each"]
df["Day"] = df["Order Date"].dt.day_name()
df["Month"] = df["Order Date"].dt.month_name()
df["YearMonth"] = df["Order Date"].dt.to_period("M")

df["City"] = (
    df["Purchase Address"].str.split(",").str[1].str.strip()
)

df["State"] = df["Purchase Address"].str.extract(
    r",\s*([A-Z]{2})\s+\d{5}"
)

# SIDEBAR
st.sidebar.title("Dashboard Filters")

cities = sorted(df["City"].dropna().unique())

selected_city = st.sidebar.multiselect(
    "Select City",
    cities,
    default=cities
)

data = df[df["City"].isin(selected_city)].copy()

if data.empty:
    st.warning("No data available for selected cities.")
    st.stop()

# KPI SECTION
st.subheader("Business Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Sales", f"${data['Sales'].sum():,.2f}")
c2.metric("Total Orders", f"{data['Order ID'].nunique():,}")
c3.metric("Total Quantity", f"{data['Quantity Ordered'].sum():,}")
c4.metric("Average Sales", f"${data['Sales'].mean():,.2f}")

st.divider()

# QUESTION 1
st.header("1. Which day of the week has the highest sales?")

day_sales = (
    data.groupby("Day")["Sales"]
    .sum()
    .reindex([
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ])
    .dropna()
)

best_day = day_sales.idxmax()

st.success(f"Answer: {best_day} has the highest sales.")

fig1 = px.bar(
    x=day_sales.index,
    y=day_sales.values,
    labels={"x": "Day", "y": "Total Sales"},
    title="Total Sales by Day",
    text_auto=".2s"
)

st.plotly_chart(fig1, use_container_width=True)

st.divider()

# QUESTION 2
st.header("2. Which product has the highest average quantity per order?")

avg_quantity = (
    data.groupby("Product")["Quantity Ordered"]
    .mean()
    .sort_values(ascending=False)
)

best_product = avg_quantity.idxmax()

st.success(
    f"Answer: {best_product} has the highest average quantity."
)

fig2 = px.bar(
    x=avg_quantity.values,
    y=avg_quantity.index,
    orientation="h",
    labels={
        "x": "Average Quantity",
        "y": "Product"
    },
    title="Average Quantity by Product"
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# QUESTION 3
st.header("3. Which state brings in the most sales?")

state_sales = (
    data.groupby("State")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

best_state = state_sales.idxmax()

st.success(
    f"Answer: {best_state} generates the highest sales."
)

fig3 = px.bar(
    x=state_sales.index,
    y=state_sales.values,
    labels={
        "x": "State",
        "y": "Total Sales"
    },
    title="Total Sales by State"
)

st.plotly_chart(fig3, use_container_width=True)

st.divider()

# QUESTION 4
st.header("4. Which products are the most popular in each city?")

city_product = (
    data.groupby(["City", "Product"])["Quantity Ordered"]
    .sum()
    .reset_index()
)

popular_products = city_product.loc[
    city_product.groupby("City")["Quantity Ordered"].idxmax()
].sort_values("Quantity Ordered", ascending=False)

st.success("Answer: Most popular product in each city.")

st.dataframe(
    popular_products,
    use_container_width=True,
    hide_index=True
)

fig4 = px.bar(
    popular_products,
    x="City",
    y="Quantity Ordered",
    color="Product",
    title="Most Popular Products by City",
    labels={"Quantity Ordered": "Total Quantity"}
)

st.plotly_chart(fig4, use_container_width=True)

st.divider()

# QUESTION 5
st.header(
    "5. Which month had the lowest sales, "
    "and which product caused the drop?"
)

monthly_sales = (
    data.groupby("YearMonth")["Sales"]
    .sum()
    .sort_index()
)

lowest_month = monthly_sales.idxmin()

product_sales = (
    data.groupby(["YearMonth", "Product"])["Sales"]
    .sum()
    .unstack(fill_value=0)
)

previous_month = lowest_month - 1

if previous_month in product_sales.index:

    product_change = (
        product_sales.loc[lowest_month]
        - product_sales.loc[previous_month]
    )

    lowest_product = product_change.idxmin()
    biggest_drop = product_change.min()

    st.success(
        f"Lowest Sales Month: {lowest_month}\n\n"
        f"Product with biggest sales drop: {lowest_product}"
    )

    st.write(
        f"Sales change compared to previous month: "
        f"${biggest_drop:,.2f}"
    )

else:
    st.info(
        "Previous calendar month is not available "
        "for comparison in this filtered dataset."
    )

fig5 = px.line(
    x=monthly_sales.index.astype(str),
    y=monthly_sales.values,
    markers=True,
    labels={
        "x": "Month",
        "y": "Total Sales"
    },
    title="Monthly Sales Trend"
)

st.plotly_chart(fig5, use_container_width=True)

st.divider()

# DATA PREVIEW
st.header("📋 Sales Dataset")
st.dataframe(data, use_container_width=True)

# DOWNLOAD
st.download_button(
    "Download Sales Data",
    data.to_csv(index=False),
    file_name="sales_analysis.csv",
    mime="text/csv"
)
