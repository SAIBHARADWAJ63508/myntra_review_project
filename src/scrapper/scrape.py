from flask import request
from selenium import webdriver
from selenium.webdriver.common.by import By
from src.exceptions import CustomException
from bs4 import BeautifulSoup as bs
import pandas as pd
import os,sys
import time
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote

class ScrapeReviews:
    def __init__(self,
                 product_name:str,
                 no_of_products:int):
        options=Options()
        self.driver=webdriver.Chrome(options=options)

        self.product_name=product_name
        self.no_of_products=no_of_products

    def scrape_product_urls(self,product_name):
        try:
            search_string=product_name.replace(" ","-")

            encoded_query=quote(search_string)

            self.driver.get(
                f"https://www.myntra.com/{search_string}?rawQuery={encoded_query}"
            )
            myntra_text=self.driver.page_source
            myntra_html=bs(myntra_text,"html.parser")
            pclass=myntra_html.find_all("ul",{"class":"results-base"})

            product_urls=[]
            for i in pclass:
                href=i.find_all("a",href=True)

                for product_no in range(len(href)):
                    t=href[product_no]["href"]
                    product_urls.append(t)

            return product_urls
        
        except Exception as e:
            raise CustomException(e,sys)
        

    def extract_reviews(self,product_link):
        try:
            productLink="https://www.myntra.com/"+product_link
            self.driver.get(productLink)
            prodRes=self.driver.page_source
            prodRes_html=bs(prodRes,"html.parser")
            title_h=prodRes_html.find_all("title")

            self.product_title=title_h[0].text

            overallRating=prodRes_html.find_all(
                "div",{"class":"index-overallRating"}
            )
            for i in overallRating:
                self.prod_rating_value=i.find("div").text
            price=prodRes_html.find_all("span",{"class":"pdp-price"})
            for i in price:
                self.product_price=i.text
            product_reviews=prodRes_html.find(
                "a",{"class":"detailed-reviews-allReviews"}
            )

            if not product_reviews:
                return None
            return product_reviews
        except Exception as e:
            raise CustomException(e,sys)
        

    def scroll_to_load_reviews(self):
        self.driver.set_window_size(1920,1080)

        last_height=self.driver.execute_script("return document.body.scrollHeight")  

        while True:
            self.driver.execute_script("window.scrollBy(0,1000);")
            time.sleep(3) 

            new_height=self.driver.execute_script("return document.body.scrollHeight")

            if new_height==last_height:  
                break

            last_height=new_height   


    def extract_products(self,product_reviews:list):
        try:
            t2=product_reviews["href"]
            Review_link="https://www.myntra.com"+t2
            self.driver.get(Review_link)

            self.scroll_to_load_reviews()

            review_page=self.driver.page_source
            review_html=bs(review_page,"html.parser")
            review=review_html.find_all(
                "div",{"class":"user-review-main user-review-showRating"}
            )

            for i in review:
                user_rating=i.find_all(
                    "div",{"class":"user-review-main user-review-showRating"}
                )
                user_comment=i.find_all(
                    "div",{"class":"user-review-reviewTextWrapper"}
                )
                user_name=i.find_all(
                    "div",{"class":"user-review-left"})
                
            reviews=[]
            for i in range(len(user_rating)):
                try:
                    rating=(
                        user_rating[i]
                        .find("span",class_="user-review-starRating")
                        .get_text()
                        .strip()
                    )

                except:
                    rating="No rating Given"

                try:
                    comment=user_comment[i].text
                except:
                    comment="No comment Given"
                try:
                    name=user_name[i].find("span").text
                except:
                    name="No name given"
                try:
                    date=user_name[i].find_all("span")[1].text
                except:
                    date="no date given"

                mydict={
                    "product Name":self.product_title,
                    "Over_All_Rating": self.prod_rating_value,
                    "Price":self.product_price,
                    "Date":date,
                    "Rating": rating,
                    "Name": name,
                    "Comment":comment,
                }
                reviews.append(mydict)

            review_data=pd.DataFrame(
                reviews,
                columns=[
                    "product Name",
                    "Over_All_Rating",
                    "Price",
                    "Date",
                    "Rating",
                    "Name",
                    "Comment"
                ],
            )

            return review_data
        
        except Exception as e:
            raise CustomException(e,sys)
    
    
    def skip_products(self,search_string,no_of_products,skip_index):
        product_urls:list=self.scrape_product_urls(search_string,no_of_products)

        product_urls.pop(skip_index)

    def get_review_data(self)->pd.DataFrame:
        try:
            product_urls=self.scrape_product_urls(product_name=self.product_name)

            product_details=[]
            review_len=0

            while review_len< self.no_of_products:
                product_url= product_urls[review_len]
                review=self.extract_reviews(product_url)

                if review:
                    product_detail=self.extract_products(review)
                    product_details.append(product_detail)

                    review_len+=1
                else:
                    product_urls.pop(review_len)
            self.driver.quit()

            data=pd.concat(product_details, axis=0)

            data.to_csv("data.csv",index=False)

            return data
        except Exception as e:
            raise CustomException(e,sys)



                
    
    