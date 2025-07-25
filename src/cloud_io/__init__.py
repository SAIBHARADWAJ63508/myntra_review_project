import pandas as pd
from src.database_connect import mongo_operation as mongo # Correct import
import os, sys
from src.constants import *
from src.exceptions import CustomException
from dotenv import load_dotenv
load_dotenv()



class MongoIO:
    mongo_ins = None

    def __init__(self):
        if MongoIO.mongo_ins is None:
            mongo_db_url = os.getenv("MONGO_DB_URL")
            if mongo_db_url is None:
                raise Exception(f"Environment key: {MONGODB_URL_KEY} is not set.")
            MongoIO.mongo_ins = mongo(client_url=mongo_db_url,
                                      database_name=MONGO_DATABASE_NAME)
        self.mongo_ins = MongoIO.mongo_ins

    def store_reviews(self, product_name: str, reviews: pd.DataFrame): # Explicitly type-hint reviews as DataFrame
        try:
            if reviews.empty:
               raise ValueError("No reviews to store.")

            collection_name = product_name.replace(" ", "_")
            # --- PREVIOUSLY: review_docs = reviews.to_dict(orient="records") ---
            # --- CORRECTED LINE: Pass the DataFrame directly as the 'dataframe' argument ---
            self.mongo_ins.bulk_insert(collection_name=collection_name, dataframe=reviews)
            print("Stored Data into mongodb") # Debug statement

        except Exception as e:
           raise CustomException(e, sys)


    def get_reviews(self,
                    product_name: str):
        try:
            data = self.mongo_ins.find(
                collection_name=product_name.replace(" ", "_")
            )

            return data

        except Exception as e:
            raise CustomException(e, sys)