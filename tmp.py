import os
import re

import base64
import pandas as pd
import oracledb
import psycopg2
from config.db_config import db_info




for db in db_info.keys():
    db_info[db]['password'] = base64.b64decode(db_info[db]['password']).decode('utf-8')

### DATABASE CONNECTIONS ###

def get_db(db: str):
    '''Get database connection object. Either oracledb or psycopg2 conn type.'''
    conn = None
    if db in ['waffles', 'waffles_selene', 'protein']:
        conn = psycopg2.connect(**db_info[db])
    
    elif db in ['dotmatics']:
        conn = oracledb.connect(**db_info[db])
    return conn


class PKStudy():
    def __init__(self):
        self.conn = get_db('dotmatics')
        #self.sp_query = select * from

    def pk_param_by_sp(self, sp_list):

        # Construct the SQL query with placeholders for the list elements
        # Create a bind variable for the list
        bind_var = {f"bind{i}": val for i, val in enumerate(sp_list)}

        # Construct the SQL query with placeholders for the list elements
        placeholders = ", ".join(f":bind{i}" for i in range(len(sp_list)))
        sql_query = f"SELECT * FROM DS3_USERDATA.SB_PK_PARAMETERS WHERE COMPOUND_ID_ORIGINAL IN ({placeholders})"

        # Execute the query and fetch the results into a pandas DataFrame
        df_pk = pd.read_sql_query(sql_query, self.conn, params=bind_var)
        return df_pk
    
    def SP_list(self):
        sql_query = f"SELECT UNIQUE (COMPOUND_ID_ORIGINAL) AS BIOREG_ID FROM DS3_USERDATA.SB_PK_PARAMETERS"
        df_SP = pd.read_sql_query(sql_query, self.conn)
        return df_SP
    
    def study_by_sp(self, sp_list):
        
        # Construct the SQL query with placeholders for the list elements
        # Create a bind variable for the list
        bind_var = {f"bind{i}": val for i, val in enumerate(sp_list)}

        # Construct the SQL query with placeholders for the list elements
        placeholders = ", ".join(f":bind{i}" for i in range(len(sp_list)))
        sql_query = f"SELECT * FROM DS3_USERDATA.SB_CONC_DATA WHERE COMPOUND_ID IN ({placeholders})"

        # Execute the query and fetch the results into a pandas DataFrame
        data_frame = pd.read_sql_query(sql_query, self.conn, params=bind_var)
        
        return data_frame
    
    def study_all(self):
        
        # Construct the SQL query with placeholders for the list elements
        # Create a bind variable for the list
        sql_query = f"SELECT * FROM DS3_USERDATA.SB_CONC_DATA"
        # Execute the query and fetch the results into a pandas DataFrame
        data_frame = pd.read_sql_query(sql_query, self.conn)
        
        return data_frame
    
    def std_compound_id(self, SP):
        sp_fields = SP.split('-')
        if len(sp_fields) <= 2:
            return SP
        else:
            return f"{sp_fields[0]}-{sp_fields[1]}"

    def pk_param_all(self, filter=True):
        # Construct the SQL query with placeholders for the list elements
        # Create a bind variable for the list
        if filter:
            sql_query = f"SELECT * FROM DS3_USERDATA.SB_PK_PARAMETERS WHERE ANALYTE_TYPE = 'TAB' and DAY = 'D1'"
        else:
            sql_query = f"SELECT * FROM DS3_USERDATA.SB_PK_PARAMETERS"
        # Execute the query and fetch the results into a pandas DataFrame
        data_frame = pd.read_sql_query(sql_query, self.conn)
        data_frame['STRAIN'] = data_frame['STRAIN'].str.strip()
        data_frame['COMPOUND_ID'] = data_frame['COMPOUND_ID'].apply(lambda x: self.std_compound_id(x))

        return data_frame


pk = PKStudy()

df_time_conc = pk.study_all()

df_time_conc.to_excel('pk_study_all.xlsx')
# print(df_time_conc)