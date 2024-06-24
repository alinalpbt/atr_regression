import pandas as pd
import numpy as np
import config

'''
计算资金曲线、年化收益率、回撤
'''
# 计算资金曲线函数
def calculate_equity_curve(df):
    equity_curve = []  # 存储每笔交易后的资金情况
    current_equity = config.initial_capital  # 初始资金等于初始本金

    for index, row in df.iterrows():
        if row['capital_investment'] != position # 仓位变化（买入或卖出）时
            trade_profit = (row['sell_price'] - row['buy_price']) * abs(row['capital_investment'] - position)  # 根据买入价、卖出价和仓位变化来计算盈亏金额
            current_equity += trade_profit  # 调整当前资金
            position = row['position']  # 更新当前仓位

        equity_curve.append(current_equity)  # 将每次交易后的资金情况加入列表

    # 将资金曲线添加到DataFrame中
    df['equity_curve'] = equity_curve

    final_equity = equity_curve[-1]  # 最后的资金

    return df['equity_curve'], final_equity

# 计算年化收益函数
def calculate_annualized_return(df):
    total_return = (df['capital_investment'].iloc[-1] / df['capital_investment'].iloc[0]) - 1
    total_days = (df['time'].iloc[-1] - df['time'].iloc[0]).days      # 假设time列是Python的datetime类型
    total_days = max(total_days, 1)      # 防止投资时间小于一天导致的错误
    annualized_return = (1 + total_return) ** (365 / total_days) - 1      # 年化收益率计算公式
    return annualized_return

# 计算最大回撤函数
def calculate_max_drawdown(df):
    equity_curve = df['capital_investment'] / df['capital_investment'].iloc[0]
    peak = equity_curve.cummax()
    drawdown = (equity_curve - peak) / peak
    max_drawdown = drawdown.min()
    return max_drawdown

# 实际计算
def evaluate_performance(file_path):
    df = pd.read_csv(file_path)

    # 将 'time' 列转换为 datetime 类型
    df['time'] = pd.to_datetime(df['time'])
    
    # 计算各项指标
    equity_curve, final_equity = calculate_equity_curve(df) 
    annualized_return = calculate_annualized_return(df)
    max_drawdown = calculate_max_drawdown(df)

    # 输出结果
    print(f"最后资金: {final_equity:.2f}")    
    print(f"年化收益率: {annualized_return:.2%}")
    print(f"最大回撤: {max_drawdown:.2%}")
    
    # 返回资金曲线供进一步使用
    return equity_curve