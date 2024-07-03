import backtrader as bt
import config

'''
策略：atr_regression 和 buyandhold
'''

class ATR_Regression_Strategy(bt.Strategy):
    params = config.strategy_params

    def __init__(self):
        self.ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=config.strategy_params['ema_period'])
        self.atr = bt.indicators.AverageTrueRange(self.data, period=config.strategy_params['atr_period'])
        self.order = None
        self.buy_count = 0  
        self.sell_count = 0 
        self.last_trade_price = None  # 记录上一次交易的价格

    def calculate_y(self, x, ema200, atr):
        atr_multiplier = config.strategy_params['atr_multiplier']
        if x >= ema200 + atr_multiplier * atr:
            return 50
        elif x <= ema200 - atr_multiplier * atr:
            return 200
        else:
            delta_atr = (x - ema200) / atr
            if delta_atr > 0:
                return 100 - 5 * (delta_atr // 2)
            else:
                return 100 + 10 * (abs(delta_atr) // 2)

    def next(self):
        if self.order:
            return
        
        # 只有在均线计算完成后才开始交易
        if len(self.data) < self.params.ema_period:
            return
        
        x = self.data.close[0]
        ema200 = self.ema[0]
        atr = self.atr[0]

        # 如果这是第一次交易，直接记录价格并返回
        if self.last_trade_price is None:
            self.last_trade_price = x
            return

        # 检查价格是否超出上次交易价格的2ATR范围
        if abs(x - self.last_trade_price) < 2 * atr:
            return        

        y = self.calculate_y(x, ema200, atr)
        target_position = self.broker.get_cash() / x * (y / 100)
        current_position = self.broker.getposition(self.data).size

        if current_position < target_position:
            self.order = self.buy(size=target_position - current_position)
            self.order.addinfo(x=x, ema200=ema200, atr=atr, y=y, target_position=target_position, current_position=current_position)
            self.last_trade_price = x  # 更新最后交易价格
        elif current_position > target_position:
            self.order = self.sell(size=current_position - target_position)
            self.order.addinfo(x=x, ema200=ema200, atr=atr, y=y, target_position=target_position, current_position=current_position)
            self.last_trade_price = x  # 更新最后交易价格

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_count += 1
            elif order.issell():
                self.sell_count += 1

        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None

class BuyAndHoldStrategy(bt.Strategy):
    def __init__(self):
        self.buy_count = 0
        self.sell_count = 0
        self.order = None  
        self.buy_executed = False
        self.sell_executed = False

    def next(self):
        # 在第一个可交易的 bar 买入
        if len(self) == 1 and not self.position and not self.buy_executed:
            self.order = self.buy()
            self.buy_executed = True

        # 判断是否达到倒数第二个bar
        if len(self) == self.data.total_lines - 2 and self.position and not self.sell_executed:
            self.order = self.sell()
            self.sell_executed = True

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                # self.log('BUY COMPLETED, Price: %.2f' % order.executed.price)
                self.buy_count += 1
            elif order.issell():
                # self.log('SELL COMPLETED, Price: %.2f' % order.executed.price)
                self.sell_count += 1
            self.order = None

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))