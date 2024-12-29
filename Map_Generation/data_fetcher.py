# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 20:04:33 2024

@author: marbo
"""

import pandas as pd
from influxdb_client import InfluxDBClient
import pickle
import os


class DataFetcher:
    """
    A class to fetch data from InfluxDB.

    Attributes:
        qtok (str): Query token for the InfluxDB query.
        pie (str): Foot side ("Right" or "Left").
        start_date (str): The start date for the query.
        end_date (str): The end date for the query.
        token (str): InfluxDB token.
        org (str): InfluxDB organization name.
        url (str): InfluxDB URL.
        verbose (int): Verbosity level to control output.
        
    Methods:
        build_query(): Constructs the InfluxDB query.
        fetch_data(): Fetches data from InfluxDB and returns a pandas DataFrame.
    """
    
    def __init__(self, qtok, pie, start_date, end_date, token, org, url, \
                    database, retention, verbose=0) -> None:
        self.qtok = qtok
        self.pie = pie
        self.start_date = start_date
        self.end_date = end_date
        self.token = token
        self.org = org
        self.url = url
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.verbose = verbose
        self.bucket = database+"/"+retention
        self.database = database
        self.retention = retention
        
    def build_query(self):
        """
        Builds the query for InfluxDB based on the parameters provided.

        Returns:
            str: The constructed query string.
        """
        metrics = ['Ax', 'Ay', 'Az', 'Gx', 'Gy', 'Gz', 'Mx', 'My', 'Mz', 'S0', 'S1', 'S2', 'lat', 'lng']
        metrics_str = ' or '.join([f'r._field == "{metric}"' for metric in metrics])
        columns_str = ', '.join([f'"{metric}"' for metric in metrics])

        query = f'''
        from(bucket: "{self.bucket}")
        |> range(start: time(v: "{self.start_date}"), stop: time(v: "{self.end_date}"))
        |> filter(fn: (r) => r._measurement == "{self.database}")
        |> filter(fn: (r) => {metrics_str})
        |> filter(fn: (r) => r["CodeID"] == "{self.qtok}" and r["type"] == "SCKS" and r["Foot"] == "{self.pie}")
        |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> keep(columns: ["_time", {columns_str}])
        '''
        
        # query = f'''
        #     from(bucket:"Gait/autogen")
        #     |> range(start: {self.start_date}, stop: {self.end_date})
        #     |> filter(fn: (r) => r["_measurement"] == "Gait")
        #     |> filter(fn: (r) => r["CodeID"] == "{self.qtok}" and r["type"] == "SCKS" and r["Foot"] == "{self.pie}")
        #     |> filter(fn: (r) => r["_field"] == "S0")
        #     |> yield()
        #     '''
        
        if self.verbose > 1:
            print(f"Constructed Query: {query}")
        return query
    
    def fetch_data(self):
        """
        Fetches data from the InfluxDB based on the query parameters provided.
    
        This method performs the following steps:
            1. Prints a message indicating the start of data fetching, if verbosity is enabled.
            2. Builds a query string for fetching data from InfluxDB based on provided parameters.
            3. Executes the query using the InfluxDB client.
            4. Aggregates the results into a pandas DataFrame.
            5. Resets the DataFrame index to ensure a clean structure.
            6. Prints information about the fetched data if verbosity level is set to 1 or higher.
    
        Returns:
        -------
        pd.DataFrame
            A DataFrame containing the fetched data with columns corresponding to the records 
            retrieved from InfluxDB.

        """  
        if self.verbose > 0:
            print(f"\nFetching data for token: {self.qtok}, Foot: {self.pie}, from {self.start_date} to {self.end_date}")
        
        
        query = self.build_query()
        
        if self.verbose > 1:
            print("Executing query...")
            
        result = self.client.query_api().query(org=self.org, query=query)
        res = pd.DataFrame()
        
        
        for i in result:
            rs = [row.values for row in i.records]
            res = pd.concat([res, pd.DataFrame(rs)], axis=0)
        res.reset_index(drop=True, inplace=True)
        
        if self.verbose > 0:
            print("Data fetching complete.")
        
        if self.verbose > 1:
            print(f"Fetched data size: {res.shape}")
        return res
    
    def save_to_pickle(self, df, output_dir='data', filename='movements_df.pkl'):
        """
        Saves the DataFrame to a pickle file.

        Parameters:
        ----------
        df : pd.DataFrame
            The DataFrame to save.
        output_dir : str
            The directory where the file should be saved.
        filename : str
            The name of the pickle file.
        """
        # Create the output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(df, f)
            if self.verbose > 0:
                print(f"DataFrame successfully saved to {filepath}")
            if self.verbose > 1:
                print(f"Pickle file saved with {len(df)} records.")
        except Exception as e:
            if self.verbose > 0:
                print(f"Failed to save DataFrame to {filepath}.")
            if self.verbose > 1:
                print(f"Error details: {str(e)}")
