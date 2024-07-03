import backtrader as bt

'''
自定义的，解析长期持仓策略的分析器
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

            # 将已关闭交易的盈亏添加到列表
            if trade_info['closed']:
                self.pnl.append(trade_info['pnl'])  

    def notify_trade(self, trade):
        if trade.isclosed:
            for t in self.trades:
                if t['date'] == bt.num2date(trade.dtclose):
                    t['closed'] = True
                    t['pnl'] = trade.pnl
                    break

    def get_analysis(self):
        total_return = sum(self.pnl)
        if self.strategy.broker.startingcash > 0:  # 防止除以零
            total_return_percent = total_return / self.strategy.broker.startingcash
        else:
            total_return_percent = 0
        
        annual_return = (1 + total_return_percent) ** (365.0 / len(self.pnl)) - 1 if len(self.pnl) > 0 else 0
        max_drawdown = min(self.pnl) if self.pnl else 0
        sharpe_ratio = np.mean(self.pnl) / np.std(self.pnl) if len(self.pnl) > 1 and np.std(self.pnl) != 0 else 0

        return {
            'trades': self.trades,
            'total_return': total_return,
            'total_return_percent': total_return_percent,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
        }