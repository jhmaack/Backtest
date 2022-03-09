#### MODULE LOADING

## 1) BASIC                     ----------------------------------------
import datetime
import numpy as np
import pandas as pd

# load module that is collection of build in functions
# e.g. MAs, Bollinger Bands, Keltner Channel, etc.


## 2) Load Supporting Functions for Strategy        --------------------

import strat_support_functions as functions


## 3) FUNCTIONS                 ----------------------------------------
def strat_01_start():
    '''
    starting point for the backtester
    '''
    return int(400)



def strat_01(data, pos, rules, stop_loss, s_avg_time = 3):
    '''
    function which receives as input the dataframe of the data
    and the dataframe of the position of the strategy.
    The outputs are two: one is the signals dictionary showing the next 
    move of the strategy, the other is a number (or NaN) showing
    the current performance of the current active trade
    '''
    signals = {'Asset':'future',"Quant":0,'ent_l':0,'ent_s':0,'ex_l':0,'ex_s':0}
    
    
    pct_gain = np.nan
    
    if pos.In == 1:
        if pos.Long == 1:
            pct_gain = ((data.Close[-1] * pos.Quant) / (pos.Beg_Price * pos.Quant) -1) * 100
        else:
            pct_gain = ((pos.Beg_Price * pos.Quant)/(data.Close[-1] * pos.Quant)-1) * 100
    
    

    ## Exit condition -> if we are
    if pos.In == 1 and not stop_loss:
        
        # Strategy Closing Signal
        if pos.Long == 1:
            if pct_gain >= 6:
                signals['ex_l']  = 1
                signals['Quant'] = 1
                
        if pos.Short == 1:
            if pct_gain >= 6:
                signals['ex_s']  = 1
                signals['Quant'] = 1
            

    ## Enter
    if pos.In == 0:     # assuming just one possible enter per time
        # Strategy Buy Signal 1: cross above the Simple MA with s_avg_time periods
        if data.Close[-2] <= data.Close.rolling(s_avg_time).mean()[-2] and data.Close[-1] >= data.Close.rolling(s_avg_time).mean()[-1]:
            signals['ent_l']  = 1
            signals['Quant'] = 1
        # Strategy Sell Signal 1: cross below the Simple MA with s_avg_time periods
        if data.Close[-2] >= data.Close.rolling(s_avg_time).mean()[-2] and data.Close[-1] <= data.Close.rolling(s_avg_time).mean()[-1]:
            signals['ent_s']  = 1
            signals['Quant'] = 1
                            
    
    return signals, pct_gain
