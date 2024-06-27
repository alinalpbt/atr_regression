import backtrader as bt

class ATR_Regression_Strategy(bt.Strategy):
    params = (
        ('ema_period', 200),
        ('atr_period', 14),
        ('atr_multiplier', 20),
        ('commission_rate', 0.0005),
        ('slippage', 0.001),
    )

    def __init__(self):
        self.ema = {d._name: bt.indicators.ExponentialMovingAverage(d.close, period=self.params.ema_period) for d in self.datas}
        self.atr = {d._name: bt.indicators.AverageTrueRange(d, period=self.params.atr_period) for d in self.datas}
        self.order = {d._name: None for d in self.datas}

    def log(self, txt, dt=None):
        pass  # 禁用日志记录

    def next(self):
        for data in self.datas:
            if self.order[data._name]:
                continue

            current_position = self.broker.getposition(data=data).size
            target_position = self.get_target_position(data)
            if target_position != current_position:
                self.order[data._name] = self.order_target_size(data=data, target=target_position)

    def get_target_position(self, data):
        size = self.broker.get_cash() / data.close[0]
        upper_band = self.ema[data._name][0] + self.params.atr_multiplier * self.atr[data._name][0]
        lower_band = self.ema[data._name][0] - self.params.atr_multiplier * self.atr[data._name][0]

        if data.close[0] == self.ema[data._name][0]:
            return size
        elif data.close[0] <= upper_band and data.close[0] > self.ema[data._name][0]:
            return size * (1 - 0.5 * (data.close[0] - self.ema[data._name][0]) / (upper_band - self.ema[data._name][0]))
        elif data.close[0] >= lower_band and data.close[0] < self.ema[data._name][0]:
            return size * (1 + (self.ema[data._name][0] - data.close[0]) / (self.ema[data._name][0] - lower_band))
        return 0

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            for data in self.datas:
                if order.data is data:
                    self.order[data._name] = None
