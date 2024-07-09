import glob
import os

'''
用于修改参数
'''

# 获取 results 文件夹中的所有 CSV 文件
data_dir = 'results'
data_files = [(os.path.splitext(os.path.basename(file))[0], file) for file in glob.glob(os.path.join(data_dir, '*.csv'))]

# 资金、佣金、滑点设置
initial_cash = 10000
commission_rate = 5/10000
slippage = 1/1000

# 策略参数
strategy_params = {
    'ema_period': 200,
    'atr_period': 14,
    'atr_multiplier': 20
}