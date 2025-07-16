import streamlit as st
import pandas as pd
from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY # Make sure this is correctly imported from src.constants

st.set_page_config("Myntra Analysis")
st.title("Myntra Review Analysis")

# 1. Try to get data directly from session_state (most recent scrape)
product_name = st.session_state.get(SESSION_PRODUCT_KEY, "") # Get product name safely
analysis_data = st.session_state.get("scraped_reviews_df", pd.DataFrame()) # Get scraped DataFrame safely

# 2. If session_state is empty, try to fetch from MongoDB
if analysis_data.empty and product_name:
    st.info(f"No recent scraped data found in session. Attempting to fetch reviews for '{product_name}' from MongoDB...")
    mongo_con = MongoIO()
    try:
        # get_reviews will return a list of dicts based on your MongoIO implementation
        db_data_list = mongo_con.get_reviews(product_name=product_name)
        if db_data_list: # Check if the list from DB is not empty
            analysis_data = pd.DataFrame(db_data_list)
            st.success(f"Successfully loaded {len(analysis_data)} reviews for '{product_name}' from MongoDB.")
        else:
            st.warning(f"No reviews found for '{product_name}' in MongoDB.")
    except Exception as e:
        st.error(f"Error fetching data from MongoDB: {e}")
        analysis_data = pd.DataFrame() # Ensure data is empty if there's an error

# 3. Perform analysis only if data is available
if not analysis_data.empty:
    st.subheader(f"Analysis for: {product_name if product_name else 'Unknown Product'}")
    st.write(f"Total reviews found: {len(analysis_data)}")

    # Display a sample of the data
    st.subheader("Sample Reviews Data")
    st.dataframe(analysis_data.head())

    # --- Your Analysis Logic Goes Here ---
    # Example: Basic rating distribution
    st.subheader("Rating Distribution")
    if 'Rating' in analysis_data.columns:
        # Convert 'Rating' column to numeric, handling "No rating Given"
        analysis_data['Rating_Numeric'] = pd.to_numeric(
            analysis_data['Rating'].str.replace(' out of 5', ''), errors='coerce'
        )
        rating_counts = analysis_data['Rating_Numeric'].value_counts().sort_index()
        st.bar_chart(rating_counts)
    else:
        st.info("No 'Rating' column found for distribution analysis.")

    # Example: Price information
    st.subheader("Product Price Information")
    if 'Price' in analysis_data.columns:
        unique_prices = analysis_data['Price'].unique()
        if len(unique_prices) == 1:
            st.write(f"The product price is: **{unique_prices[0]}**")
        else:
            st.write(f"Multiple prices observed: {', '.join(unique_prices)}")
    else:
        st.info("No 'Price' column found.")

    # You can add more complex analysis here (sentiment, word clouds, etc.)

else:
    st.warning("No data available for analysis. Please scrape reviews first from the main page.")
    # Optional: Display a link or button to go back to the main app
    # if st.button("Go back to Scraper"):
    #     st.session_state["page"] = "scraper" # You'd need a page management system for this