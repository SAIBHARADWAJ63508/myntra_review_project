import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import os,sys
from src.exceptions import CustomException

class DashboardGenerator:
    def __init__(self,data):
        self.data=data
    
    def display_general_info(self):
        st.header('General information')

        self.data['Over_All_Rating']=pd.to_numeric(self.date['Over_All_Rating'],errors='coerce')
        self.data['Price']=pd.to_numeric(
            self.data['Price'].apply(lambda x:x.replace("₹","")),
            errors='coerce')
        
        self.data["Rating"]=pd.to_numeric(self.data['Rating'],errors='coerce')

        product_ratings=self.data.groupby('Product Name', as_index=False)['Over_All_Rating'].mean().dropna()

        fig_pie=px.pie(product_ratings,values='Over_All_Rating',names='Product Name',
                       title='Average Ratings by Product')
        st.plotly_chart(fig_pie)

        avg_prices=self.data.groupby('Product Name',as_index=False)['Price'].mean().dropna()
        fig_bar=px.bar(avg_prices,x='Product Name',y='Price', color='Product Name' ,
                       title='Average Price Comparison Between Products',
                       color_discrete_sequence=px.colors.qualitative.Bold)
        
        fig_bar.update_xaxes(title='Product Name')
        fig_bar.update_yaxes(title='Average Price')
        st.plotly_chart(fig_bar)

    def display_product_sections(self):
        st.header('Product Sections')
        product_names=self.data['Product Name'].unique()
        columns=st.columns(len(product_names))

        for i, product_name in enumerate(product_names):
            product_data=self.data[self.data['Product Name']==product_name]

            with columns[i]:
                st.subheader(f'{product_name}')

                avg_price=product_data['Price'].mean()
                st.markdown(f"Average Price: ₹{avg_price:.2f}")

                avg_rating=product_data['Over_All_Rating'].mean()
                st.markdown(f"Average Rating:{avg_rating:.2f}")

                positive_reviews=product_data[product_data['Rating']>=4.5].nlargest(5,'Rating')
                st.subheader('Positive Reviews')
                for index, row in positive_reviews.iterrows():
                    st.markdown(f" Rating:{row['Rating']}-{row['Comment']}")

                negative_reviews=product_data[product_data['Rating']<=2].nsmallest(5,'Rating')
                st.subheader('Negative Reviews')
                for index, row in negative_reviews.iterrows():
                    st.markdown(f"Rating:{row['Rating']}- {row['Comment']}")

                    st.subheader('Rating Counts')

                    rating_counts=product_data['Rating'].value_counts().sort_index(ascending=False)
                    for rating, count in rating_counts.items():
                        st.write(f"* Rating{rating} count:{count}")
                        



            