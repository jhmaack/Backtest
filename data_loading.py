import datetime
import pandas as pd
'''
Function which takes as input raw data an 
give as output a pandas dataframe with the original 
data and other elaborations of those.
'''

def get(data_name,loud=0):

    if type(data_name) != str: data_name = str(data_name)

    try:        
        df = pd.read_csv(data_name,parse_dates=[['Date', 'Time']])
        df.index = df['Date_Time']
        df['Volume'] = df['Up'] + df['Down']
        df['AvgPrice'] = round(df.loc[:,['Open','High','Low','Close']].mean(axis=1),5) 
        df['Range'] = df['High'] - df['Low']
        df['MidPrice'] = round((df['High'] + df['Low']) / 2 ,5)
        df['MidBodyPrice'] = round((df['Open'] + df['Close']) / 2 ,5)
        del df['Date_Time']
        del df['Up']
        del df['Down']

        if loud ==1:
            print('Loading successfull. File loaded: ',data_name)
            print(df.info())

        return df
        
    except:
        print('Error loading data.')
