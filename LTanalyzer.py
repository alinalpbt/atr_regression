import backtrader as bt
import numpy as np
import math

'''
自定义的，解析长期持仓策略的分析器
LongTermTradeAnalyzer用于输出单笔交易数据
CalculateAnalyzer用于计算总收益率、年化收益率、最大回撤、夏普比率
'''

class LongTermTradeAnalyzer(bt.Analyzer):
    def __init__(self):
        self.trades = []
        self.pnl = []  # 存储每笔交易的盈亏

    def notify_order(self, order):
        if order.status in [order.Completed]:
            trade_info = {
                'date': bt.num2date(order.executed.dt),
                'price': order.executed.price,
                'size': order.executed.size,
                'value': order.executed.value,
                'pnl': order.executed.pnl,
                'isbuy': order.isbuy(),
                'closed': False,
                'x': order.info.get('x', None),
                'ema200': order.info.get('ema200', None),
                'atr': order.info.get('atr', None),
                'y': order.info.get('y', None),
                'target_position': order.info.get('target_position', None),
                'current_position': order.info.get('current_position', None)
            }
            self.trades.append(trade_info)

    def notify_trade(self, trade):
        if trade.isclosed:
            for t in self.trades:
                if t['date'] == bt.num2date(trade.dtclose):
                    t['closed'] = True
                    t['pnl'] = trade.pnl
                    self.pnl.append(trade.pnl)  # 记录已关闭交易的盈亏
                    break

    def get_analysis(self):
        return {
            'trades': self.trades,
            'pnl': self.pnl
        }
    
# 计算总收益
class CalculateTotalReturn(bt.Analyzer):
    def __init__(self):
        self.start_value = None
        self.end_value = None

    def start(self):
        if self.start_value is None:
            self.start_value = self.strategy.broker.get_value()
            
    def stop(self):
        if self.end_value is None:
            self.end_value = self.strategy.broker.get_value()
           
    def get_analysis(self):
        # 计算总收益率
        total_return = (self.end_value - self.start_value) / self.start_value

        return {
            'total_return': total_return
        }

class CalculateAnnualReturn(bt.Analyzer):
    def __init__(self):
        self.start_value = None
        self.end_value = None
        self.start_date = None
        self.end_date = None

    def start(self):
        if self.start_value is None:
            self.start_value = self.strategy.broker.get_value()
            if len(self.strategy.data.datetime.array):
                # 获取初始日期
                self.start_date = bt.num2date(self.strategy.data.datetime.array[0]).date()

    def stop(self):
        if self.end_value is None:
            self.end_value = self.strategy.broker.get_value()
            if len(self.strategy.data.datetime.array):
                # 获取结束日期
                self.end_date = bt.num2date(self.strategy.data.datetime.array[-1]).date()


    def get_analysis(self):
        # 计算总收益
        total_return_analyzer = self.strategy.analyzers.total_return.get_analysis()
        total_return = total_return_analyzer['total_return']
        
        # 计算总周期时间
        if self.start_date and self.end_date:
            days = (self.end_date - self.start_date).days
            years = days / 365.0
        else:
            days = 1
            years = days / 365.0  # 默认值，防止除以零错误
        
        # 计算年化
        if years > 0:
            annual_return = (1 + total_return) ** (1 / years) - 1
        else:
            annual_return = total_return

        return {
            'annual_return': annual_return
        }
    
# 计算最大回撤
class CalculateMaxDrawdown(bt.Analyzer):
    def __init__(self):
        self.max_drawdown = 0
        self.peak = -math.inf

    def next(self):
        value = self.strategy.broker.get_value()
        if value > self.peak:
            self.peak = value
        drawdown = (self.peak - value) / self.peak
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown

    def get_analysis(self):
        return {
            'max_drawdown': self.max_drawdown
        }

# # 计算夏普
# class CalculateSharpeRatio(bt.Analyzer):
#     def __init__(self, risk_free_rate=0.0):
#         self.risk_free_rate = risk_free_rate
#         self.returns = []

#     def next(self):
#         value = self.strategy.broker.get_value()
#         if len(self.returns) > 0:
#             daily_return = (value - self.returns[-1]) / self.returns[-1]
#             self.returns.append(daily_return)
#         else:
#             self.returns.append(value)

#     def get_analysis(self):
#         returns = self.returns[1:]
#         mean_return = sum(returns) / len(returns)
#         excess_returns = [r - self.risk_free_rate / 252 for r in returns]  # assuming 252 trading days in a year
#         std_dev = math.sqrt(sum([r ** 2 for r in excess_returns]) / (len(excess_returns) - 1))
#         sharpe_ratio = mean_return / std_dev * math.sqrt(252) if std_dev != 0 else 0
#         return {
#             'sharpe_ratio': sharpe_ratio
#         }