#!/usr/bin/env python
# coding: utf-8

# In[93]:


import jqdatasdk as jd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
import backtrader as bt


# In[94]:

jd.auth('13347072270', 'Hjw1010848870@')

# In[91]:

df = jd.get_bars('IF9999.CCFX', 1000, unit='10m',fields=['date','open','close','high','low','volume'],include_now=False,end_dt='2024-06-10')
df = pd.DataFrame(df)
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace = True)
print(df)

fig, axlist = mpf.plot(df, type = 'candle', style = 'charles', volume = True, title = 'K-line chart', ylabel = 'price', ylabel_lower = 'volume', mav = (3,6), figratio = (10,6), figscale = 1.2, returnfig = True)


# In[32]:


def detect_fvg(data):
    fvg_zones = []
    for i in range(2, len(data) - 1):
        high_curr = data['high'][i]
        low_curr = data['low'][i]
        high_prev2 = data['high'][i - 2]
        low_prev2 = data['low'][i - 2]
        high_nxt = data['high'][i + 1]
        low_nxt = data['low'][i + 1]

        if low_curr > high_prev2:
            fvg_zones.append({'type': 'bullish', 'start': high_prev2, 'end': low_curr, 'index': i})
        elif high_curr < low_prev2:
            fvg_zones.append({'type': 'bearish', 'start': low_prev2, 'end': high_curr, 'index': i})

    return fvg_zones


# In[45]:


fvg_zones = detect_fvg(df)
fvg_zones


# In[86]:


def detect_ifvg(data, fvg_zones):
    signals = []

    for i in range(len(fvg_zones) - 1):
        trend = fvg_zones[i]['type']
        upper_limit, lower_limit = max(fvg_zones[i]['start'], fvg_zones[i]['end']), min(fvg_zones[i]['start'], fvg_zones[i]['end'])
        idx, idx_nxt = fvg_zones[i]['index'], fvg_zones[i + 1]['index']

        if trend == 'bullish':
            for j in range(idx + 1, idx_nxt):
                if min(df.iloc[j]['open'], df.iloc[j]['close']) < lower_limit:
                    for k in range(j + 1, idx_nxt):
                        left_low = min(df.iloc[k]['open'], df.iloc[k]['close']) < min(df.iloc[k + 1]['open'], df.iloc[k + 1]['close'])
                        right_low = min(df.iloc[k + 2]['open'], df.iloc[k + 2]['close']) < min(df.iloc[k + 1]['open'], df.iloc[k + 1]['close'])

                        if left_low and right_low:
                            signals.append('sell')
               
        elif trend == 'bearish':
            for j in range(idx + 1, idx_nxt):
                if max(df.iloc[j]['open'], df.iloc[j]['close']) > upper_limit:
                    for k in range(j + 1, idx_nxt):
                        left_high = max(df.iloc[k]['open'], df.iloc[k]['close']) > max(df.iloc[k + 1]['open'], df.iloc[k + 1]['close'])
                        right_high = max(df.iloc[k + 2]['open'], df.iloc[k + 2]['close']) > max(df.iloc[k + 1]['open'], df.iloc[k + 1]['close'])

                        if left_high and right_high:
                            signals.append('buy')
                
    return signals

print(detect_ifvg(df, fvg_zones))


# In[87]:


def trade_logic(data, fvg_zones):
    signals = detect_ifvg(data, fvg_zones)
    
    for signal in signals:
        if signal == 'buy':
            # 买入
            print("买入信号触发: 做多")
        
        if signal == 'sell':
            # 做空
            print("卖出信号触发: 做空")

trade_logic(df, fvg_zones)

