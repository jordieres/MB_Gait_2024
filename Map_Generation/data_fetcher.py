# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 20:04:33 2024

@author: marbo
"""

import pandas as pd
from influxdb_client import InfluxDBClient

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
    
    def __init__(self, qtok, pie, start_date, end_date, token, org, url, verbose=0):
        self.qtok = qtok
        self.pie = pie
        self.start_date = start_date
        self.end_date = end_date
        self.token = token
        self.org = org
        self.url = url
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.verbose = verbose
        
    def build_query(self):
        """
        Builds the query for InfluxDB based on the parameters provided.

        Returns:
            str: The constructed query string.
        """
        query = f'''
        from(bucket:"Gait/autogen")
        |> range(start: {self.start_date}, stop: {self.end_date})
        |> filter(fn: (r) => r["_measurement"] == "Gait")
        |> filter(fn: (r) => r["CodeID"] == "{self.qtok}" and r["type"] == "SCKS" and r["Foot"] == "{self.pie}")
        |> filter(fn: (r) => r["_field"] == "S0")
        |> yield()
        '''
        if self.verbose > 1:
            print(f"Constructed Query: {query}")
        return query
    
    def fetch_data(self):
        
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
