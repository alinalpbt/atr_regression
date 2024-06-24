import os

'存储所有参数设置'

# 数据文件目录
folder_path = os.path.abspath(os.path.dirname(__file__)) # 返回当前文件夹路径
data_path = r'D:\code\100CODE\ATR_regression\data'
file_type = 'csv'
output_path = r'D:\code\100CODE\ATR_regression\results'

# 基础参数
initial_capital = 10000 # 初始资金
leverage_rate = 1  # 杠杆
slippage = 1 / 1000  # 滑点
C_rate = 5 / 10000  # 手续费
# MIN_MARGIN_RATIO = 2 / 100  # 最低保证金率
# FACE_VALUE = 0.00001 

# 回测时间
# STRATEGY_START = '2018-01-01'  # 回测开始时间
# STRATEGY_END = '2024-04-01'  # 回测结束时间

# 股票/证券符号 & 时间周期
tickers = ['SPY', 'QQQ', '000300']
timeframes = ['4h']

# 策略
strategy = "ATR_regression"

# 参数
params_list = [
    {'ema_period': 200, 'atr_period': 14, 'atr_multiplier': 20}
]