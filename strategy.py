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

    def next(self):
        if self.order:
            return

        # 获取当前持仓和目标持仓
        current_position = self.broker.getposition(self.data).size
        target_position = self.get_target_position()

        # 如果当前持仓与目标持仓不同，执行买入操作
        if current_position < target_position:
            self.order = self.buy(size=target_position - current_position)
            self.buy_count += 1  
        elif current_position > target_position:
            self.order = self.sell(size=current_position - target_position)
            self.sell_count += 1

    def get_target_position(self):
        close = self.data.close[0]
        ema = self.ema[0]
        atr = self.atr[0]
        atr_multiplier = config.strategy_params['atr_multiplier']
        step = config.strategy_params['step']

        upper_band = ema + atr_multiplier * atr
        lower_band = ema - atr_multiplier * atr

        # 默认持仓量
        capital_investment = 1.0

        if close >= upper_band:
            capital_investment = 0.5
        elif close <= lower_band:
            capital_investment = 2.0
        elif ema < close < upper_band:
            for i in range(step, atr_multiplier, step):
                capital_investment = 1.0 - 0.5 * i / atr_multiplier
                break
        elif lower_band < close < ema:
            for i in range(step, atr_multiplier, step):
                capital_investment = 1.0 + i / atr_multiplier
                break

        return self.broker.get_cash() / close * capital_investment

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None