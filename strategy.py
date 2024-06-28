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

        current_position = self.broker.getposition(self.data).size
        target_position = self.get_target_position()

        if target_position != current_position:
            if target_position > current_position:
                self.order = self.buy(size=target_position - current_position)
                self.buy_count += 1  
            elif target_position < current_position:
                self.order = self.sell(size=current_position - target_position)
                self.sell_count += 1  

    def get_target_position(self):
        size = self.broker.get_cash() / self.data.close[0]
        close = self.data.close[0]
        ema = self.ema[0]
        atr = self.atr[0]
        atr_multiplier = config.strategy_params['atr_multiplier']

        upper_band = ema + atr_multiplier * atr
        lower_band = ema - atr_multiplier * atr

        # 默认100%本金
        capital_investment = 1.0

        if close == upper_band:
            capital_investment = 0.5
        elif close == lower_band:
            capital_investment = 2.0
        else:
            steps = int(atr_multiplier / 2)  # 每2ATR调整一次

        # 从上轨到EMA
        if close > ema and close < upper_band:
            capital_investment = 1.0 - 0.5 * ((close - ema) / (upper_band - ema))
        
        # 从EMA到下轨
        elif close < ema and close > lower_band:
            capital_investment = 1.0 + 1.0 * ((ema - close) / (ema - lower_band))

        return size * capital_investment  # 计算目标持仓量


    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None