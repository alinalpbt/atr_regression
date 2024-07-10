import backtrader as bt
import config
from indicators import VWMA

'''
策略
'''

class VADStrategy(bt.Strategy):
    params = (
        ('k', config.vad_strategy_params['k']),
        ('base_order_amount', config.vad_strategy_params['base_order_amount']),
        ('dca_multiplier', config.vad_strategy_params['dca_multiplier']),
        ('number_of_dca_orders', config.vad_strategy_params['number_of_dca_orders'])
    )

    def __init__(self):
        self.atr = bt.indicators.ATR(self.data, period=14) #这个要改成 Indicator里的指标
        self.vwma = VWMA(self.data, period=config.indicator_params['vwma_period'])
        self.k_atr = self.params.k * self.atr
        self.take_profit_percent = self.params.k * self.atr
        self.stop_loss_percent = self.params.k * self.atr
        self.add_long_counter = 1
        self.last_dca_price = 0.0
        self.total_long_trades = 0
        self.buy_count = 0
        self.sell_count = 0

    def next(self):
        vwma_above = self.vwma.vwma[0] + self.k_atr[0]
        vwma_below = self.vwma.vwma[0] - self.k_atr[0]
        long_signal = self.data.close[0] < vwma_below
        short_signal = self.data.close[0] > vwma_above
        
        # 开仓逻辑
        if long_signal and self.total_long_trades == 0:
            size = self.params.base_order_amount / self.data.close[0]
            self.buy(size=size)
            self.last_dca_price = self.params.base_order_amount
            self.total_long_trades = 1
            self.buy_count += 1
            self.log(f'Buy order: Size={size}, Price={self.data.close[0]}')

        # 加仓逻辑
        elif long_signal and self.total_long_trades > 0 and self.total_long_trades < self.params.number_of_dca_orders:
            self.last_dca_price *= self.params.dca_multiplier
            size = self.last_dca_price / self.data.close[0]
            self.buy(size=size)
            self.add_long_counter += 1
            self.total_long_trades += 1
            self.buy_count += 1
            self.log(f'Additional Buy order: Size={size}, Price={self.data.close[0]}')

        # 计算未平仓利润
        if self.position.size > 0:
            cost_basis = self.position.price
            current_price = self.data.close[0]

            # 止盈止损
            if short_signal and current_price - cost_basis >= self.take_profit_percent[0] * self.position.size:
                self.sell(size=self.position.size)
                self.sell_count += 1
                self.log(f'Sell order (Take Profit): Size={self.position.size}, Price={self.data.close[0]}')

            elif short_signal and current_price - cost_basis <= - self.take_profit_percent[0] * self.position.size:
                self.sell(size=self.position.size)
                self.sell_count += 1
                self.log(f'Sell order (Stop Loss): Size={self.position.size}, Price={self.data.close[0]}')

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')

class BuyAndHoldStrategy(bt.Strategy):
    def __init__(self):
        self.buy_count = 0
        self.sell_count = 0
        self.order = None  
        self.buy_executed = False
        self.sell_executed = False
        # self.log(f'Initial Cash: {self.broker.get_cash()}')

    def next(self):
        # 在第一个可交易的 bar 买入
        if len(self) == 1 and not self.position and not self.buy_executed:
            cash = self.broker.get_cash()
            close_price = self.data.close[0]
            commission_rate = config.broker_params['commission_rate']
            slippage_rate = config.broker_params['slippage']

            # 计算总成本
            size = int(cash / (close_price * (1 + commission_rate + slippage_rate)))
            total_cost = size * close_price * (1 + commission_rate + slippage_rate)
            
            # self.log(f'Trying to buy: Cash={cash}, Close={close_price}, Size={size}, Total Cost={total_cost}')
            if total_cost <= cash and size > 0:
                self.order = self.buy(size=size)
                self.buy_executed = True
                # self.log(f'Buy order created: Size={size}')

        # 判断是否达到倒数第二个bar
        if len(self) == self.data.total_lines - 2 and self.position and not self.sell_executed:
            # self.log(f'Trying to sell: Position Size={self.position.size}')
            self.order = self.sell(size=self.position.size)
            self.sell_executed = True

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                # self.log(f'BUY COMPLETED, Price: {order.executed.price}, Size: {order.executed.size}')
                self.buy_count += 1
            elif order.issell():
                # self.log(f'SELL COMPLETED, Price: {order.executed.price}, Size: {order.executed.size}')
                self.sell_count += 1
            self.order = None
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            # self.log(f'Order Canceled/Margin/Rejected: Status={order.status}, Ref={order.ref}')
            self.order = None

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')


# class AR_Strategy(bt.Strategy):
#     params = config.atr_regression_params

#     def __init__(self):
#         self.ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=config.strategy_params['ema_period'])
#         self.atr = bt.indicators.AverageTrueRange(self.data, period=config.strategy_params['atr_period'])
#         self.order = None
#         self.buy_count = 0  
#         self.sell_count = 0 
#         self.last_trade_price = None  # 记录上一次交易的价格

#     def calculate_y(self, x, ema200, atr):
#         # 计算目标仓位比例 y
#         atr_multiplier = config.strategy_params['atr_multiplier']
#         if x >= ema200 + atr_multiplier * atr:
#             return 50  # 如果价格x高于 ema200 + atr_multiplier * atr, 返回50%
#         elif x <= ema200 - atr_multiplier * atr:
#             return 200  # 如果价格x低于 ema200 - atr_multiplier * atr, 返回200%
#         else:
#             delta_atr = (x - ema200) / atr  # 当前价格与均线之间的差值相对于 ATR 的倍数
#             if delta_atr > 0: # 如果delta为正，则价格高于ema200，目标仓位要减少
#                 return 100 - 5 * (delta_atr // 2) # 每2个atr，仓位减少5%
#             else:
#                 return 100 + 10 * (abs(delta_atr) // 2) # 每2个atr，仓位增加10%

#     def next(self):
#         # 检查是否有活动订单，如果有则跳过
#         if self.order:
#             return
        
#         # 只有在均线计算完成后才开始交易
#         if len(self.data) < self.params.ema_period:
#             return
        
#         x = self.data.close[0] # 当前收盘价
#         ema200 = self.ema[0] # 当前 ema 值
#         atr = self.atr[0] # 当前 atr 值

#         # 如果这是第一次交易，直接记录价格并返回
#         if self.last_trade_price is None:
#             self.last_trade_price = x
#             return

#         # 检查价格是否超出上次交易价格的 2 ATR 范围
#         if abs(x - self.last_trade_price) < 2 * atr:
#             return        

#         y = self.calculate_y(x, ema200, atr)  # 目标仓位比例
#         target_position = config.initial_cash / x * (y / 100) # 计算目标持仓数量
#         current_position = self.broker.getposition(self.data).size # 获取当前持仓数量

#         # 如果当前持仓小于目标持仓，则买入差额部分
#         if current_position < target_position:
#             self.order = self.buy(size=target_position - current_position)
#             self.order.addinfo(x=x, ema200=ema200, atr=atr, y=y, target_position=target_position, current_position=current_position)
#             self.last_trade_price = x  # 更新最后交易价格

#         # 如果当前持仓大于目标持仓，则卖出差额部分
#         elif current_position > target_position:
#             self.order = self.sell(size=current_position - target_position)
#             self.order.addinfo(x=x, ema200=ema200, atr=atr, y=y, target_position=target_position, current_position=current_position)
#             self.last_trade_price = x  # 更新最后交易价格

#     def notify_order(self, order):
#         # 处理订单状态变化
#         if order.status in [order.Completed]:
#             # 记录买卖次数
#             if order.isbuy():
#                 self.buy_count += 1
#             elif order.issell():
#                 self.sell_count += 1

#         # 如果订单完成、取消或出现保证金问题，则重置当前订单
#         if order.status in [order.Completed, order.Canceled, order.Margin]:
#             self.order = None