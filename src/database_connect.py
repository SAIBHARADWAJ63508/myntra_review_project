# In src/database_connect.py

import pymongo
import pandas as pd

class mongo_operation:
    def __init__(self, client_url: str, database_name: str):
        self.client_url = client_url
        self.database_name = database_name

    def get_client(self):
        """Creates a client connection to MongoDB."""
        return pymongo.MongoClient(self.client_url)

    def get_database(self):
        """Gets the database from the client."""
        client = self.get_client()
        return client[self.database_name]

    def get_collection(self, collection_name: str):
        """Gets a collection from the database."""
        db = self.get_database()
        return db[collection_name]

    def bulk_insert(self, collection_name: str, dataframe: pd.DataFrame):
        """
        Inserts a pandas DataFrame into the specified collection.
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("The 'dataframe' argument must be a pandas DataFrame.")
            
        collection = self.get_collection(collection_name)
        # Convert dataframe to a list of dictionaries (records)
        records = dataframe.to_dict('records')
        
        if records:
            collection.insert_many(records)
            print(f"Successfully inserted {len(records)} records into '{collection_name}'.")
        else:
            print("DataFrame is empty, nothing to insert.")

    def find(self, collection_name: str, query: dict = None):
        """
        Finds documents in a collection and returns them as a pandas DataFrame.
        """
        if query is None:
            query = {} # Find all documents if no query is provided
            
        collection = self.get_collection(collection_name)
        cursor = collection.find(query)
        df = pd.DataFrame(list(cursor))
        
        # MongoDB adds an '_id' column by default, you may want to remove it
        if '_id' in df.columns:
            df = df.drop(columns=['_id'])
            
        return df