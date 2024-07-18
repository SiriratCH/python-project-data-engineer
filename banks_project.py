from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd 
import numpy as np 
import sqlite3
import requests

# Task 1, 7
def log_progress(message): 
    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second 
    now = datetime.now() # get current timestamp 
    timestamp = now.strftime(timestamp_format) 
    with open(log_file,"a") as f: 
        f.write(timestamp + ' : ' + message + '\n') 


# Task 2
def extract(url, table_name): 
    page = requests.get(url).text
    data = BeautifulSoup(page, 'html.parser')
    df = pd.DataFrame(columns=table_attribs)

    tables = data.find_all('tbody')
    rows = tables[0].find_all('tr')
    
    for row in rows: 
        col = row.find_all('td')
        if len(col) != 0: 
            ancher_data = col[1].find_all('a')[1]['title']
            if ancher_data is not None:
                data_dict = {
                    "Name": ancher_data,
                    "MC_USD_Billion": col[2].contents[0][:-1]
                }
                df1 = pd.DataFrame(data_dict, index=[0])
                df = pd.concat([df,df1], ignore_index=True)

    return df


# Task 3
def transform(df):
    df_exchange = pd.read_csv("./exchange_rate.csv")
    exchange_rate = df_exchange.set_index('Currency').to_dict()['Rate']

    USD_list = df['MC_USD_Billion'].to_list()
    USD_list = [float(''.join(x.split('\n'))) for x in USD_list]
    df['MC_USD_Billion'] = USD_list

    df['MC_GBP_Billion'] = [np.round(x*exchange_rate['GBP'],2) for x in df['MC_USD_Billion']]
    df['MC_EUR_Billion'] = [np.round(x*exchange_rate['EUR'],2) for x in df['MC_USD_Billion']]
    df['MC_INR_Billion'] = [np.round(x*exchange_rate['INR'],2) for x in df['MC_USD_Billion']]
    
    return df

# Task 4
def load_to_csv(df, csv_path):
    df.to_csv(csv_path)


# Task 5
def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists='replace', index=False)

# Task 6
def run_queries(query_statement, sql_connection):
    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)



url = 'https://web.archive.org/web/20230908091635%20/https://en.wikipedia.org/wiki/List_of_largest_banks'
table_attribs = ['Name', 'MC_USD_Billion']
csv_path = './Largest_banks_data.csv'
db_name = 'Banks.db'
table_name = 'Largest_banks'
log_file = './code_log.txt'


log_progress('Preliminaries complete. Initiating ETL process')
df = extract(url, table_attribs)

# Task 2b extract
# print(df)

log_progress('Data extraction complete. Initiating Transformation process')
df = transform(df)

# Task 3b transform
# print(df['MC_EUR_Billion'][4])

log_progress('Data transformation complete. Initiating loading process')
load_to_csv(df, csv_path)

log_progress('Data saved to CSV file')
sql_connection = sqlite3.connect('Banks.db')

log_progress('SQL Connection initiated.')
load_to_db(df, sql_connection, table_name)

log_progress('Data loaded to Database as table. Running the query')

query_statement = "SELECT * from Largest_banks" 
run_queries(query_statement, sql_connection)

query_statement = "SELECT AVG(MC_GBP_Billion) FROM Largest_banks"
run_queries(query_statement, sql_connection)

query_statement = "SELECT Name from Largest_banks LIMIT 5"
run_queries(query_statement, sql_connection)

log_progress('Process Complete.')

sql_connection.close()
log_progress('Server Connection closed.')

