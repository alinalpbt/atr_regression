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
            self.order.x = x
            self.order.ema200 = ema200
            self.order.atr = atr
            self.order.y = y
            self.order.target_position = target_position
            self.order.current_position = current_position
            self.buy_count += 1
            self.last_trade_price = x  # 更新最后交易价格
        elif current_position > target_position:
            self.order = self.sell(size=current_position - target_position)
            self.order.x = x
            self.order.ema200 = ema200
            self.order.atr = atr
            self.order.y = y
            self.order.target_position = target_position
            self.order.current_position = current_position
            self.sell_count += 1
            self.last_trade_price = x  # 更新最后交易价格

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
        # if len(self) <= 2:  # 打印前两根 K 线的信息
        #     print(f"当前索引: {len(self)}, 日期时间: {self.data.datetime.datetime(0)}, 开盘价: {self.data.open[0]}, 收盘价: {self.data.close[0]}")
        
        if len(self) == 1 and not self.position:  # 在第一个可交易的 bar 买入
            self.order = self.buy()
            self.buy_count += 1
            self.buy_executed = True

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f' % order.executed.price)
            self.order = None

    def stop(self):
        if self.position:
            self.order = self.sell()
            self.sell_count += 1
        # self.trade_log_file.close()  # 关闭文件

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))