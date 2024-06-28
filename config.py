# 数据文件
data_files = [
    ("QQQ", "C:/github/atr_regression/results/processed_BATS_QQQ.csv"),
    ("SPY", "C:/github/atr_regression/results/processed_BATS_SPY.csv"),
    ("000300", "C:/github/atr_regression/results/processed_SSE_DLY_000300.csv")
]

# 资金、佣金、滑点设置
initial_cash = 10000
commission_rate = 0.0005
slippage = 0.001

# 策略参数
strategy_params = {
    'ema_period': 200,
    'atr_period': 14,
    'atr_multiplier': 20,
    'step': 2,
    'up_change': 50 / 100,
    'down_change': 100 / 100
}