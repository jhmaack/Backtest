
# IMPORTS
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def backtest(dataframe, rules, strat, strat_start, end= 2000, fees = 0.05):
    '''
    backtesting function.
    input are the data as pandas df, the rules as dictionary
    starting and end point and value for fees
    output is the pandas df with the performance of every trade
    '''

    # ****************** INITIALIZATION PHASE ****************** #

    start = strat_start()                   # Grabs starting time from strategy script
    # length = len(dataframe) - start       # Not used. Ommit last period, so that profit calculation can be made
    
    # Dummy for stop loss activation
    Stop_Loss = False

    
    # Create pos-dataframe and P&L dataframe 
    pos = pd.DataFrame(index = dataframe.index)
    pos['AType'] = ''
    pos['In'] = np.nan
    pos['Long'] = np.nan
    pos['Short'] = np.nan
    pos['Quant'] = np.nan
    pos['Beg_Price'] = np.nan
    pos['Open_PnL'] = np.nan


    profit_loss = pd.DataFrame(columns=['DateTimeIn','DateTimeOut','BuyPrice','SellPrice','ProfitLoss'])

    # Assign value of t-1 period for strategy function
    pos.AType.iloc[start-1] = 'future'
    pos.In.iloc[start-1] = 0
    pos.Long.iloc[start-1] = 0
    pos.Short.iloc[start-1] = 0
    pos.Quant.iloc[start-1] = 0
    pos.Beg_Price.iloc[start-1] = np.nan
    pos.Open_PnL.iloc[start-1] = np.nan

    
    ## START BACKTESTING ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    for i in range(start,end-1):
        curr_date = dataframe.index[i]
        next_date = dataframe.index[i+1]

        # STRATEGY BLOCK 
        # 2 outputs: signals and open_pnl which can be a number or Nan
        signals, open_pnl = strat(dataframe.iloc[0:i+1], pos.iloc[i-1], rules, Stop_Loss, 100)        # Give previous position to strategy
        print(signals)
        # Update position dataframe. Step 1: Setup for period. Copy values from previous period
        pos.iloc[i] = pos.iloc[i-1]
        pos.Open_PnL.iloc[i] = open_pnl

        ### EXECUTION

        # Enter Long
        if signals['ent_l'] == 1:
            pos.In.iloc[i]     = 1
            pos.Long.iloc[i]   = 1
            pos.Quant.iloc[i]  = 1
            pos.Beg_Price.iloc[i] = dataframe.Open[next_date]
            dateIn_tmp = next_date
            
        # Stop Loss Long side
        # Stop loss is implemented via dummy Stop_Loss in 2 consecutive iteration.
        # In the first just activate the dummy, in the second update the fields and reset the dummy.
        if Stop_Loss == True and pos.Long.iloc[i]==1:
            pos.In.iloc[i]     = 0
            pos.Long.iloc[i]   = 0
            pos.Quant.iloc[i]  = 0
            pos.Beg_Price.iloc[i] = np.nan
                
            # Save profit. Note that sometimes the stop loss is due to a gap at the opening and the actual loss would be greater than SL
            if (dataframe.Open[curr_date] - pos.Beg_Price.iloc[i-1]) / pos.Beg_Price.iloc[i-1] * 100 <= -rules['SL']:
                profit = (dataframe.Open[curr_date] - pos.Beg_Price.iloc[i-1]) / pos.Beg_Price.iloc[i-1] * 100 - 2*fees
            else:
                profit = -rules['SL'] - 2*fees
            profit_loss = profit_loss.append({'DateTimeIn': dateIn_tmp, 
                                            'DateTimeOut': curr_date,
                                            'BuyPrice':pos.Beg_Price.iloc[i-1],
                                            'SellPrice':pos.Beg_Price.iloc[i-1]*(1+profit/100),
                                            'ProfitLoss': profit}, ignore_index=True)
            
            pos.Open_PnL.iloc[i] = np.nan
            Stop_Loss = False
        
        # Condition for stop loss. If there is already and exit signal the latter has priority because it happens before.
        if pos.Long.iloc[i] == 1 and signals['ex_l']!=1:
            if (dataframe.Low[next_date] - pos.Beg_Price.iloc[i]) / pos.Beg_Price.iloc[i] * 100 <= -rules['SL']:
                Stop_Loss = True

                
        # Exit Long
        if signals['ex_l'] == 1:
            
            # Save profit
            profit = (dataframe.Open[next_date] - pos.Beg_Price.iloc[i-1]) / pos.Beg_Price.iloc[i-1] * 100 - 2*fees
            profit_loss = profit_loss.append({'DateTimeIn': dateIn_tmp, 
                                            'DateTimeOut': next_date, 
                                            'BuyPrice':pos.Beg_Price.iloc[i-1], 
                                            'SellPrice':dataframe.Open[next_date], 
                                            'ProfitLoss': profit}, ignore_index=True)

            pos.In.iloc[i]     = 0
            pos.Long.iloc[i]   = 0
            pos.Quant.iloc[i]  = 0
            pos.Beg_Price.iloc[i] = np.nan


        # Enter Short
        if signals['ent_s'] == 1:
                
            pos.In.iloc[i]     = 1
            pos.Short.iloc[i]  = 1
            pos.Quant.iloc[i]  = 1
            pos.Beg_Price.iloc[i] = dataframe.Open[next_date]
            dateIn_tmp = next_date
            
            
        # Stop Loss Short
        if Stop_Loss == True and pos.Short.iloc[i]==1:
            pos.In.iloc[i]     = 0
            pos.Short.iloc[i]  = 0
            pos.Quant.iloc[i]  = 0
            pos.Beg_Price.iloc[i] = np.nan
                
            if (pos.Beg_Price.iloc[i-1] - dataframe.Open[curr_date]) / pos.Beg_Price.iloc[i-1] * 100 <= -rules['SL']:
                profit = (pos.Beg_Price.iloc[i-1] - dataframe.Open[curr_date]) / pos.Beg_Price.iloc[i-1] * 100 - 2*fees
            else:
                profit = -rules['SL'] - 2*fees
            profit_loss = profit_loss.append({'DateTimeIn': dateIn_tmp, 
                                            'DateTimeOut': curr_date,
                                            'BuyPrice':pos.Beg_Price.iloc[i-1]*(1-profit/100),
                                            'SellPrice':pos.Beg_Price.iloc[i-1],
                                            'ProfitLoss': profit}, ignore_index=True)
            
            pos.Open_PnL.iloc[i] = np.nan
            Stop_Loss = False
        
        # condition for stop loss
        if pos.Short.iloc[i] == 1 and signals['ex_s']!=1:
            if (pos.Beg_Price.iloc[i] - dataframe.High[next_date]) / pos.Beg_Price.iloc[i] * 100 <= -rules['SL']:
                Stop_Loss = True
            

        # Exit Short
        if signals['ex_s'] == 1:
            
            profit = (pos.Beg_Price.iloc[i-1] - dataframe.Open[next_date]) / pos.Beg_Price.iloc[i-1] * 100 - 2*fees
            profit_loss = profit_loss.append({'DateTimeIn': dateIn_tmp, 
                                            'DateTimeOut': next_date, 
                                            'BuyPrice':dataframe.Open[next_date], 
                                            'SellPrice':pos.Beg_Price.iloc[i-1], 
                                            'ProfitLoss': profit}, ignore_index=True)
            
            pos.In.iloc[i]     = 0
            pos.Short.iloc[i]  = 0
            pos.Quant.iloc[i]  = 0
            pos.Beg_Price.iloc[i] = np.nan



    #### OUTPUT
    return profit_loss
