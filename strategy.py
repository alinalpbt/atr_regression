import backtrader as bt
import config

class ATR_Regression_Strategy(bt.Strategy):
    params = config.strategy_params

    def __init__(self):
        self.ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=config.strategy_params['ema_period'])
        self.atr = bt.indicators.AverageTrueRange(self.data, period=config.strategy_params['atr_period'])
        self.order = None
        self.buy_count = 0  
        self.sell_count = 0 

    def calculate_y(self, x, ema200, atr):
        atr_multiplier = 20
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

        x = self.data.close[0]
        ema200 = self.ema[0]
        atr = self.atr[0]
        y = self.calculate_y(x, ema200, atr)
        target_position = self.broker.get_cash() / x * (y / 100)

        current_position = self.broker.getposition(self.data).size

        if current_position < target_position:
            self.order = self.buy(size=target_position - current_position)
            self.buy_count += 1
        elif current_position > target_position:
            self.order = self.sell(size=current_position - target_position)
            self.sell_count += 1

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None

class BuyAndHoldStrategy(bt.Strategy):
    def __init__(self):
        # 初始化买卖次数计数器
        self.buy_count = 0
        self.sell_count = 0
        self.order = None  
        self.buy_executed = False

    def next(self):
        if not self.position and not self.buy_executed:
            self.order = self.buy()  # 发起买入订单
            self.buy_count += 1  # 买入次数加一
            self.buy_executed = True

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f' % order.executed.price)
                self.buy_executed = True
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f' % order.executed.price)
            self.order = None  # 订单完成后清空 order 属性

    def stop(self):
        if self.position:
            self.order = self.sell()  # 发起卖出订单
            self.sell_count += 1  # 卖出次数加一
            # self.log('SELL EXECUTED, Price: %.2f' % self.data.close[0])

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))