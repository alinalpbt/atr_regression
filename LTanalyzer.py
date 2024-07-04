import backtrader as bt
import numpy as np

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
        # 获取 LongTermTradeAnalyzer 的分析结果
        long_term_analysis = self.strategy.analyzers.longterm_trades.get_analysis()
        pnl_sum = sum(long_term_analysis['pnl'])

        # 计算总收益率
        total_return = (self.end_value - self.start_value) / self.start_value

        return {
            'total_return': total_return
        }
