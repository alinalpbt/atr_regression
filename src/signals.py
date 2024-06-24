import pandas as pd
import numpy as np
from config import *

'生成交易信号的函数'

def ATR_regression(df, params):
    ema_period = params['ema_period']
    atr_period = params['atr_period']
    atr_multiplier = params['atr_multiplier']

    # 计算EMA和ATR
    df['ema'] = df['close'].ewm(span=ema_period, adjust=False).mean()
    df['atr'] = df['close'].rolling(window=atr_period).apply(lambda x: np.max(x) - np.min(x))
    
    # 计算上下轨
    df['upper_band'] = df['ema'] + atr_multiplier * df['atr']
    df['lower_band'] = df['ema'] - atr_multiplier * df['atr']
    
    # 基本功能1：本金投资信号
    df['capital_investment'] = 1.0  # 默认100%本金
    df.loc[df['close'] == df['upper_band'], 'capital_investment'] = 0.5
    df.loc[df['close'] == df['lower_band'], 'capital_investment'] = 2.0

    # 基本功能2：均仓投入信号
    # 从上轨到EMA
    steps = atr_multiplier / 2  # 每2ATR调整一次
    for i in range(0, int(steps) + 1):
        upper_limit = df['ema'] + (atr_multiplier - 2 * i) * df['atr']
        lower_limit = df['ema'] + (atr_multiplier - 2 * (i + 1)) * df['atr']
        df.loc[(df['close'] <= upper_limit) & (df['close'] > lower_limit), 'capital_investment'] = 1.0 - (0.5 / steps * i)
    
    # 从EMA到下轨
    for i in range(0, int(steps) + 1):
        upper_limit = df['ema'] - 2 * i * df['atr']
        lower_limit = df['ema'] - 2 * (i + 1) * df['atr']
        df.loc[(df['close'] <= upper_limit) & (df['close'] > lower_limit), 'capital_investment'] = 1.0 + (1.0 / steps * i)
    
    # 基本功能3：闲置资金和新增本金投入信号
    # 此部分根据具体需求进一步定义，需要更多信息以实现

    return df

