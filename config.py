import glob
import os

'''
用于修改参数
'''

# 获取 results 文件夹中的所有 CSV 文件
data_dir = 'results'
data_files = [(os.path.splitext(os.path.basename(file))[0], file) for file in glob.glob(os.path.join(data_dir, '*.csv'))]


'''
交易所 Broker 参数设置
'''

# 资金、佣金、滑点设置
broker_params = {
    'initial_cash': 10000,
    'commission_rate': 5/10000,
    'slippage': 1/1000
}

'''
策略 Strategy 参数设置
'''

# ATR_Regression_Strategy参数
atr_regression_params = {
    'ema_period': 200,
    'atr_period': 14,
    'atr_multiplier': 20
}

# VADStrategy参数
vad_strategy_params = {
    'k': 1.6,
    'base_order_amount': 100000,
    'dca_multiplier': 1.6,
    'number_of_dca_orders': 4
}


'''
指标 Indicator 参数设置
'''

# VWMA
indicator_params = {
    'vwma_period': 14
}