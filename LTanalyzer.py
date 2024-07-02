import backtrader as bt

'''
自定义的，解析长期持仓策略的分析器
'''

class LongTermTradeAnalyzer(bt.Analyzer):
    def __init__(self):
        self.trades = []

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.trades.append({
                'date': bt.num2date(order.executed.dt),
                'price': order.executed.price,
                'size': order.executed.size,
                'value': order.executed.value,
                'pnl': order.executed.pnl,
                'isbuy': order.isbuy(),
                'closed': False,
                'x': getattr(order, 'x', None),
                'ema200': getattr(order, 'ema200', None),
                'atr': getattr(order, 'atr', None),
                'y': getattr(order, 'y', None),
                'target_position': getattr(order, 'target_position', None),
                'current_position': getattr(order, 'current_position', None)
            })

    def get_analysis(self):
        return self.trades