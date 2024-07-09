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
        total_return = total_return_analyzer['total_return'] # 直接提取总收益
        
        # 计算总周期时间
        if self.start_date and self.end_date:
            days = (self.end_date - self.start_date).days
            years = days / 365.0
        else:
            days = 1
            years = days / 365.0  # 默认值，防止除以零错误
        
        # 计算年化
        if years > 0:
            annual_return = (1 + total_return) ** (1 / years) - 1 #如果年数大于0，用复利公式计算年收益
        else:
            annual_return = total_return

        return {
            'annual_return': annual_return
        }
    
# 计算最大回撤
class CalculateMaxDrawdown(bt.Analyzer):
    def __init__(self):
        self.max_drawdown = 0 #存储最大回撤值
        self.peak = -math.inf #存储历史最高点的资产值

    def next(self):
        value = self.strategy.broker.get_value() #获取当前策略的总资产值
        if value > self.peak:
            self.peak = value
        drawdown = (self.peak - value) / self.peak # 回撤 = (历史最高点资产 - 历史最低点资产) / 历史最高点资产
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown

    def get_analysis(self):
        return {
            'max_drawdown': self.max_drawdown
        }

# 计算夏普
class CalculateSharpeRatio(bt.Analyzer):
    def __init__(self, risk_free_rate=0.02):
        self.risk_free_rate = risk_free_rate
        self.returns = [] #存储策略的每期收益值

    def next(self):
        value = self.strategy.broker.get_value()
        self.returns.append(value)

    def get_analysis(self):
        if len(self.returns) < 2:
            return {'sharpe_ratio': 0}
        
        # 计算每个4小时周期的收益率,去掉最后一个元素，计算连续资产值之间的差异
        period_returns = np.diff(self.returns) / self.returns[:-1]
        
        # 计算超额周期收益率,将无风险利率按252个交易日和每个交易日两个4小时周期调整
        excess_period_returns = period_returns - self.risk_free_rate / (252 * 2) 
        
        # 计算年化超额收益率,将超额收益率的平均值乘以每年的周期数（252天，每天两个4小时周期）
        annualized_return = np.mean(excess_period_returns) * 252 * 2
        
        # 计算年化波动率,超额收益率的标准差乘以周期数的平方根
        annualized_volatility = np.std(excess_period_returns) * np.sqrt(252 * 2)
        
        # 计算夏普比率,如果年化波动率不为零，则用年化超额收益率除以年化波动率
        sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else 0
        
        return {'sharpe_ratio': sharpe_ratio}