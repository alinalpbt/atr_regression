import backtrader as bt

'''
自定义的，解析长期持仓策略的分析器
'''

class LongTermTradeAnalyzer(bt.Analyzer):
    def __init__(self):
        self.trades = []

    def notify_order(self, order):
        if order.status in [order.Completed]:
            try:
                self.trades.append({
                    'date': bt.num2date(order.executed.dt),
                    'price': order.executed.price,
                    'size': order.executed.size,
                    'value': order.executed.value,
                    'pnl': order.executed.pnl,
                    'isbuy': order.isbuy(),
                    'closed': False,  # 长期持仓策略中没有平仓，只记录仓位变化
                })
            except Exception as e:
                print(f"Error recording order: {e}")

    def get_analysis(self):
        return self.trades