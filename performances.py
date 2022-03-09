
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def drawdown(data):
    '''
    Function which calculates the drawdown.
    Drawdown is function of the negative excursion after a new peak in the equity line
    Input is the df with the results of every trade
    '''
    data['open_equity'] = data['ProfitLoss'].cumsum()
    drawdown = []
    max_value = []
    i = 0
    while i<len(data):
        drawdown.append(0)
        max_value.append(0)
        if i>0 and float(data.open_equity[i]) > float(max_value[i-1]):
            max_value[i] = float(data.open_equity[i])
        else:
            max_value[i] = max_value[i-1]
        if i>0:
            drawdown[i] = float(data.open_equity[i]) - float(max_value[i])
        i +=1
    
    return pd.Series(drawdown)
    

def performance_report(data):
    '''
    Function with no output which prints a written report
    with the major performance parameters of the strategy.
    '''
    
    profit = data.ProfitLoss.dropna().sum()
    nop = data.ProfitLoss.dropna().count()
    gross_profit = data.ProfitLoss[data.ProfitLoss>0].dropna().sum()
    gross_loss = data.ProfitLoss[data.ProfitLoss<=0].dropna().sum()
    if gross_loss!=0:
        profit_factor = gross_profit/abs(gross_loss)
    else:
        profit_factor = gross_profit/0.000001
    avg_trade = profit/nop
    percent_win = data.ProfitLoss[data.ProfitLoss>0].dropna().count() / nop *100
    percent_loss = data.ProfitLoss[data.ProfitLoss<=0].dropna().count() / nop * 100
    avg_win = data.ProfitLoss[data.ProfitLoss>0].dropna().mean()
    avg_loss = data.ProfitLoss[data.ProfitLoss<0].dropna().mean()
    risk_rew = abs(avg_win/avg_loss)
    DD = drawdown(data)
    max_dd = DD.min()
    avg_dd = DD.dropna().mean()
    max_loss = data.ProfitLoss.dropna().min()
    max_win = data.ProfitLoss.dropna().max()
    dd_stats = DD.describe(percentiles = [0.3,0.2,0.1,0.05,0.01])
    # to be added 
    #stop_long = data.events[data.events == 'stoploss_long'].count()
    #stop_short = data.events[data.events == 'stoploss_short'].count()
    #perc_stops = round((stop_long+stop_short)/nop*100,2)
    
    print('')
    print('PERFORMANCE REPORT')
    print('')
    print('Profit: ',round(profit,2))
    print('Number of Operations: ',nop)
    print('')
    print('Profit Factor: ',round(profit_factor,2))
    print('Gross Profit: ',round(gross_profit,2))
    print('Gross Loss: ',round(gross_loss,2))
    print('')
    print('Average Trade: ',round(avg_trade,2))
    print('')
    print('Percent Winning Trades: ',round(percent_win,2))
    print('Percent Losing Trades: ',round(percent_loss,2))
    print('Risk Reward Ratio: ',round(risk_rew,2))
    print('')
    print('Max DrawDown: ',round(max_dd,2))
    print('Average Drawdown: ',round(avg_dd,2))
    print('Largest Losing Trade: ',round(max_loss,2))
    print('Largest Winning Trade: ',round(max_win,2))
    print('')
    print('Drawdown Distribution:\n',dd_stats)
    print('')
    
    
# ************************************** GRAPHICAL PART *********************************************** #


def plot_charts(data):
    '''
    Function plotting charts of the equity line, that is
    the cumulative performance of the strategy; and of the 
    Drawdown as calculated above
    '''
    plt.figure(figsize=(14, 8), dpi=80)
    plt.plot_date(data.DateTimeOut,data.ProfitLoss.cumsum(), 'b-', color='green')
    plt.axhline(y=0, color='black', linestyle='-')

    plt.xlabel("Time")
    plt.ylabel("Gain/Loss (%)")
    plt.title('Equity Line of Trading System on S')
    plt.xticks(rotation='vertical')
    plt.grid(True)
    #plt.legend()
    plt.show()
    
    
    # PART 2
    dd = drawdown(data)
    plt.figure(figsize=(14, 8), dpi=80)
    plt.plot_date(data.DateTimeOut, dd, 'b-', color='red')

    plt.fill_between(data.DateTimeOut, 0, dd, color="red")
    plt.axhline(y=dd.dropna().mean(), color='black', linestyle='-', label='Average Drawdown')
    a = np.percentile(dd, 20)
    plt.axhline(y=a, color='grey', linestyle='-', label='20 Percentile Drawdown')
    plt.xlabel('Time')
    plt.ylabel('Draw Down (%)')
    plt.title('Draw Down Chart')
    plt.xticks(rotation='vertical')
    plt.grid(True)
    plt.legend()
    plt.show()
    
