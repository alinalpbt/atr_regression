import backtrader as bt
import config

class ATR_Regression_Strategy(bt.Strategy):
    params = config.strategy_params

    def __init__(self):
        self.ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=config.strategy_params['ema_period'])
        self.atr = bt.indicators.AverageTrueRange(self.data, period=config.strategy_params['atr_period'])
        self.order = None

    def next(self):
        if self.order:
            return

        current_position = self.broker.getposition(self.data).size
        target_position = self.get_target_position()

        if target_position != current_position:
            self.order = self.order_target_size(target=target_position)

    def get_target_position(self):
        size = self.broker.get_cash() / self.data.close[0]
        upper_band = self.ema[0] + config.strategy_params['atr_multiplier'] * self.atr[0]
        lower_band = self.ema[0] - config.strategy_params['atr_multiplier'] * self.atr[0]

        if self.data.close[0] == upper_band:
            return size * 0.5
        elif self.data.close[0] == self.ema[0]:
            return size
        elif self.data.close[0] == lower_band:
            return size * 2

        if self.data.close[0] < upper_band and self.data.close[0] > self.ema[0]:
            return size * (1 - 0.5 * (self.data.close[0] - self.ema[0]) / (upper_band - self.ema[0]))
        elif self.data.close[0] > lower_band and self.data.close[0] < self.ema[0]:
            return size * (1 + (self.ema[0] - self.data.close[0]) / (self.ema[0] - lower_band))

        return 0

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.order = None
