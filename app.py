import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Set app title
st.set_page_config(page_title="Two-Wheeler Analysis Dashboard", layout="wide")
st.title("🚗 Two-Wheeler Vehicle Analysis")

# File uploader
uploaded_file = st.file_uploader("Upload the Excel file", type=["xlsx"])
if uploaded_file:
    # Read Excel
    df = pd.read_excel(uploaded_file)

    # Rename columns for cleaning
    df.columns = [
        "row_id", "brand", "model", "mode_price", "ex_showroom_price",
        "on_road_price", "color_option", "mileage_kmpl", "fuel_capacity_ltr",
        "meter_type", "gear_type", "insurance_price"
    ]

    # Clean price columns
    def clean_price(value):
        if isinstance(value, str):
            value = value.replace("₹", "").replace(",", "").replace(".", "").replace(" ", "")
        try:
            return int(value)
        except:
            return None

    price_cols = ["mode_price", "ex_showroom_price", "on_road_price", "insurance_price"]
    for col in price_cols:
        df[col] = df[col].apply(clean_price)

    # Clean mileage and fuel capacity
    def clean_float(value):
        if isinstance(value, str):
            value = value.replace("\n", "").strip()
        try:
            return float(value)
        except:
            return None

    df["mileage_kmpl"] = df["mileage_kmpl"].apply(clean_float)
    df["fuel_capacity_ltr"] = df["fuel_capacity_ltr"].apply(clean_float)

    # Drop rows with missing essential info
    df.dropna(subset=["brand", "model", "on_road_price", "mileage_kmpl", "fuel_capacity_ltr"], inplace=True)

    st.success("✅ Data cleaned successfully!")

    # ----------------------------------------
    # Sidebar Filter - Brand
    # ----------------------------------------
    st.sidebar.header("🔍 Filter Options")
    brand_options = sorted(df["brand"].dropna().unique())
    selected_brands = st.sidebar.multiselect("Select Brand(s)", brand_options, default=brand_options)

    # Filter DataFrame based on brand selection
    filtered_df = df[df["brand"].isin(selected_brands)]

    if filtered_df.empty:
        st.warning("No data available for selected brand(s). Please choose a different brand.")
    else:
        # Question 1: Top 5 most fuel-efficient two-wheelers
        st.header("1. 🛵 Top 5 Most Fuel-Efficient Two-Wheelers")
        top_mileage = filtered_df.sort_values(by="mileage_kmpl", ascending=False).head(5)
        st.dataframe(top_mileage[["brand", "model", "mileage_kmpl"]])
        fig1 = px.bar(top_mileage, x="model", y="mileage_kmpl", color="brand", title="Top Mileage Models")
        st.plotly_chart(fig1, use_container_width=True)

        # Question 2: Most Affordable Bikes (on-road price)
        st.header("2. 💸 Top 5 Most Affordable Two-Wheelers")
        cheapest = filtered_df.sort_values(by="on_road_price").head(5)
        st.dataframe(cheapest[["brand", "model", "on_road_price"]])
        fig2 = px.bar(cheapest, x="model", y="on_road_price", color="brand", title="Lowest On-Road Prices")
        st.plotly_chart(fig2, use_container_width=True)

        # Question 3: Best mileage under a user-defined budget
        st.header("3. 🎯 Best Mileage Bikes Under Your Budget")
        budget = st.slider("Select your budget (INR)", 20000, 250000, 100000, step=5000)
        budget_df = filtered_df[filtered_df["on_road_price"] <= budget].sort_values(by="mileage_kmpl", ascending=False).head(5)
        st.dataframe(budget_df[["brand", "model", "on_road_price", "mileage_kmpl"]])
        fig3 = px.bar(budget_df, x="model", y="mileage_kmpl", color="brand", title=f"Best Mileage under ₹{budget}")
        st.plotly_chart(fig3, use_container_width=True)

        # Question 4: Average mileage by brand
        st.header("4. 🏷️ Average Mileage by Brand")
        avg_mileage_brand = filtered_df.groupby("brand")["mileage_kmpl"].mean().sort_values(ascending=False).reset_index()
        fig4 = px.bar(avg_mileage_brand, x="brand", y="mileage_kmpl", title="Brand-wise Average Mileage")
        st.plotly_chart(fig4, use_container_width=True)

        # Question 5: Does higher price mean better mileage?
        st.header("5. 📈 Price vs Mileage (Is Cost Worth It?)")
        fig5 = px.scatter(filtered_df, x="on_road_price", y="mileage_kmpl", color="brand",
                          hover_data=["model"], title="On-Road Price vs Mileage")
        st.plotly_chart(fig5, use_container_width=True)

        # Question 6: Top Performers (Mileage × Fuel Capacity)
        st.header("6. 🏆 Top Bikes by Range (Mileage × Fuel Capacity)")
        filtered_df["total_range"] = filtered_df["mileage_kmpl"] * filtered_df["fuel_capacity_ltr"]
        top_range = filtered_df.sort_values(by="total_range", ascending=False).head(5)
        st.dataframe(top_range[["brand", "model", "mileage_kmpl", "fuel_capacity_ltr", "total_range"]])
        fig6 = px.bar(top_range, x="model", y="total_range", color="brand", title="Top Total Range Performers")
        st.plotly_chart(fig6, use_container_width=True)

else:
    st.info("👆 Please upload the `vehicle cost analysis2.xlsx` file to begin analysis.")
