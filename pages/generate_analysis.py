import streamlit as st
import pandas as pd
import plotly.express as px

from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY  # key used by the scraper page

st.set_page_config("Myntra Analysis")
st.title("Myntra Review Analysis")

# 1) Try to get the most recent scrape from session_state
product_name = st.session_state.get(SESSION_PRODUCT_KEY, "")
analysis_data = st.session_state.get("scraped_reviews_df", pd.DataFrame())

# 2) If session has no data, try MongoDB (get_reviews returns a DataFrame)
if analysis_data.empty and product_name:
    st.info(f"No recent scraped data in session. Trying MongoDB for '{product_name}'…")
    try:
        mongo_con = MongoIO()
        db_df = mongo_con.get_reviews(product_name=product_name)  # DataFrame
        if isinstance(db_df, pd.DataFrame) and not db_df.empty:
            analysis_data = db_df.copy()
            st.success(f"Loaded {len(analysis_data)} reviews for '{product_name}' from MongoDB.")
        else:
            st.warning(f"No reviews found for '{product_name}' in MongoDB.")
    except Exception as e:
        st.error(f"Error fetching data from MongoDB: {e}")
        analysis_data = pd.DataFrame()

# 3) Proceed only if we have data
if not analysis_data.empty:
    st.subheader(f"Analysis for: {product_name or 'Unknown Product'}")
    st.write(f"Total reviews: **{len(analysis_data)}**")

    # Show a peek of the data
    with st.expander("Preview data", expanded=False):
        st.dataframe(analysis_data.head())

    # ---------- Clean/prepare columns ----------
    # Rating: may be like "4.5 out of 5" or "No rating Given"
    if "Rating" in analysis_data.columns:
        analysis_data["Rating_Numeric"] = pd.to_numeric(
            analysis_data["Rating"].astype(str).str.extract(r"([\d.]+)")[0],
            errors="coerce"
        )
    else:
        analysis_data["Rating_Numeric"] = pd.NA

    # Price: strip ₹ and commas if present
    if "Price" in analysis_data.columns:
        analysis_data["Price_Numeric"] = pd.to_numeric(
            analysis_data["Price"].astype(str).str.replace("₹", "", regex=False).str.replace(",", "", regex=False),
            errors="coerce"
        )

    # ---------- Bar: rating distribution ----------
    st.subheader("Rating Distribution (Bar)")
    valid_ratings = analysis_data["Rating_Numeric"].dropna()
    if not valid_ratings.empty:
        rating_counts = valid_ratings.value_counts().sort_index()
        st.bar_chart(rating_counts)
    else:
        st.info("No numeric ratings available for bar chart.")

    # ---------- PIE 1: Rating buckets ----------
    st.subheader("Ratings Breakdown (Pie)")
    if not valid_ratings.empty:
        def bucketize(x: float) -> str:
            if x >= 4.0:
                return "Positive (≥4)"
            elif x >= 3.0:
                return "Neutral (3–3.9)"
            else:
                return "Negative (<3)"

        buckets = valid_ratings.apply(bucketize)
        pie_df = buckets.value_counts().rename_axis("Bucket").reset_index(name="Count")
        fig_pie_buckets = px.pie(
            pie_df,
            names="Bucket",
            values="Count",
            title="Ratings Breakdown"
        )
        st.plotly_chart(fig_pie_buckets, use_container_width=True)
    else:
        st.info("No numeric ratings to build the ratings breakdown pie chart.")

    # ---------- PIE 2: Reviews per product ----------
    st.subheader("Reviews per Product (Pie)")
    if "Product Name" in analysis_data.columns:
        product_counts = (
            analysis_data["Product Name"]
            .fillna("Unknown Product")
            .value_counts()
            .rename_axis("Product Name")
            .reset_index(name="Reviews")
        )
        if len(product_counts) > 1:
            fig_pie_products = px.pie(
                product_counts,
                names="Product Name",
                values="Reviews",
                title="Share of Reviews by Product"
            )
            st.plotly_chart(fig_pie_products, use_container_width=True)
        else:
            # Single product: pie is not meaningful
            only_name = product_counts.iloc[0, 0]
            st.write(f"All reviews are for a single product: **{only_name}**. Pie chart skipped.")
    else:
        st.info("No 'Product Name' column found for product share pie chart.")

    # ---------- Price information ----------
    st.subheader("Product Price Information")
    if "Price_Numeric" in analysis_data.columns and analysis_data["Price_Numeric"].notna().any():
        unique_prices = analysis_data["Price"].dropna().unique().tolist()
        if len(unique_prices) == 1:
            st.write(f"The product price is: **{unique_prices[0]}**")
        else:
            st.write("Multiple prices observed:")
            st.write(", ".join(map(str, unique_prices[:20])) + ("…" if len(unique_prices) > 20 else ""))
    else:
        st.info("No usable price data found.")

else:
    st.warning("No data available for analysis. Please run the scraper first from the main page.")
