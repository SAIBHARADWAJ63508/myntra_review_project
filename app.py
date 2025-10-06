import pandas as pd
import streamlit as st
from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
from src.scrapper.scrape import ScrapeReviews 



st.set_page_config(
    "myntra-review-scrapper"
)

st.title("Myntra Review Scrapper")

# Initialize session state variables if they don't exist
if SESSION_PRODUCT_KEY not in st.session_state:
    st.session_state[SESSION_PRODUCT_KEY] = ""
if "scraped_reviews_df" not in st.session_state:
    st.session_state["scraped_reviews_df"] = pd.DataFrame() # Initialize as empty DataFrame
if "data_available_for_analysis" not in st.session_state:
    st.session_state["data_available_for_analysis"] = False

def form_input():
    product = st.text_input("Search Products", value=st.session_state[SESSION_PRODUCT_KEY]) # Pre-fill with last searched product
    # Update session state immediately on input change
    if product != st.session_state[SESSION_PRODUCT_KEY]:
        st.session_state[SESSION_PRODUCT_KEY] = product
        st.session_state["data_available_for_analysis"] = False # Reset if product changes
        st.session_state["scraped_reviews_df"] = pd.DataFrame() # Clear previous data

    no_of_products = st.number_input("No of products to search",
                                     step=1,
                                     min_value=1)

    if st.button("Scrape Reviews"):
        st.session_state["data_available_for_analysis"] = False # Assume no data until proven otherwise
        st.session_state["scraped_reviews_df"] = pd.DataFrame() # Clear old data before new scrape

        scrapper = ScrapeReviews(
            product_name=product,
            no_of_products=int(no_of_products)
        )

        with st.spinner("Scraping reviews... this might take a moment."):
            scrapped_data = scrapper.get_review_data()

        if scrapped_data is not None and not scrapped_data.empty:
            st.session_state["data_available_for_analysis"] = True
            st.session_state['scraped_reviews_df'] = scrapped_data # Store the actual DataFrame!
            
            mongoio = MongoIO()
            try:
                mongoio.store_reviews(product_name=product, reviews=scrapped_data)
                st.success(f"Successfully scraped and stored {len(scrapped_data)} reviews for '{product}' into MongoDB!")
            except Exception as e:
                st.error(f"Failed to store reviews in MongoDB: {e}")
                st.warning("Analysis will proceed with currently scraped data, but it might not be persistent.")
            
            st.dataframe(scrapped_data)
        else:
            st.session_state["data_available_for_analysis"] = False
            st.session_state["scraped_reviews_df"] = pd.DataFrame()
            st.warning(f"No reviews found for '{product}' or unable to scrape. Please try a different product or adjust the number of products.")
            if scrapped_data is not None:
                 st.dataframe(scrapped_data) # Still display an empty dataframe if it's empty but not None

# The main function call
if __name__ == "__main__":
    form_input()

    # Add a button to navigate to analysis page or trigger analysis
    if st.session_state["data_available_for_analysis"]:
        st.write("---")
        st.subheader("Proceed to Analysis")
        # You can add a button here to navigate to your analysis page
        # For simplicity, let's assume the analysis logic is directly below this for now,
        # or that 'generate_analysis.py' is called as a separate Streamlit page.
        # If generate_analysis.py is a separate file, Streamlit's multipage app handles navigation.
        # The key is that it retrieves data from session_state OR MongoDB.