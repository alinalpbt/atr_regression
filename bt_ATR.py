import backtrader as bt
from backtrader.analyzers import TimeReturn, DrawDown, SharpeRatio
import pandas as pd

'''定义策略'''
class ATR_Regression_Strategy(bt.Strategy):
    '''初始化策略参数'''
    params = (
        ('ema_period', 200), #EMA周期
        ('atr_period', 14), #ATR周期
        ('atr_multiplier', 20), # ATR倍数
        ('commission_rate', 0.0005), # 佣金
        ('slippage', 0.001), #滑点
    )

    '''创建策略指标'''
    def __init__(self):
        self.ema = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.ema_period) #创建EMA(200)
        self.atr = bt.indicators.AverageTrueRange(self.data, period=self.params.atr_period) #创建ATR(14)
        self.order = None  # 当前无订单

    '''记录'''
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    '''next()为每bar调用一次的主逻辑'''
    def next(self):
        if self.order:  
            return     # 检查是否有订单进行中，如果有，就跳过后续逻辑，避免重复下单
        
        current_position = self.broker.getposition(data=self.data).size #获取当前的持仓大小
        target_position = self.get_target_position() #确定目标持仓大小
        
        if target_position != current_position: 
            self.log(f'Current Position: {current_position}, Target Position: {target_position}') # 记录
            self.order = self.order_target_size(target=target_position) # 调整持仓至目标大小

    '''计算目标持仓'''
    def get_target_position(self):
        size = self.broker.get_cash() / self.data.close[0] #size = 资金/close
        upper_band = self.ema[0] + self.params.atr_multiplier * self.atr[0] #计算上轨 ema200+20ATR
        lower_band = self.ema[0] - self.params.atr_multiplier * self.atr[0] #计算下轨 ema200-20ATR

        if self.data.close[0] == self.ema[0]: #如果close = ema200
            return size 
        elif self.data.close[0] <= upper_band and self.data.close[0] > self.ema[0]: # 如果 ema200<close<=上轨
            return size * (1 - 0.5 * (self.data.close[0] - self.ema[0]) / (upper_band - self.ema[0]))
        elif self.data.close[0] >= lower_band and self.data.close[0] < self.ema[0]: # 如果 ema200>close>=下轨
            return size * (1 + (self.ema[0] - self.data.close[0]) / (self.ema[0] - lower_band))
        return 0

    '''订单状态更新'''
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]: #如果订单完成、被取消或由于资金不足而被拒绝
            self.order = None  # 重置订单，以便发起新的交易


'''运行回测'''
data_files = {
    'QQQ': 'processed_BATS_QQQ.csv',
    'SPY': 'processed_BATS_SPY.csv',
    '000300': 'processed_SSE_DLY_000300.csv'
}

cerebro = bt.Cerebro() #初始化 Cerebro

# 添加数据和分析器
for name, file in data_files.items():
    data = bt.feeds.GenericCSVData(
        dataname=f'C:/github/atr_regression/results/{file}',
        datetime=0, open=1, high=2, low=3, close=4, volume=5,
        dtformat='%Y-%m-%d %H:%M:%S%z'
    )
    cerebro.adddata(data, name=name)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name=f'sharpe_{name}', timeframe=bt.TimeFrame.Days, data=data)
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name=f'returns_{name}', timeframe=bt.TimeFrame.Years, data=data)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name=f'drawdown_{name}', data=data)

cerebro.addstrategy(ATR_Regression_Strategy) #加载策略
cerebro.broker.setcash(10000) # 设置初始资金
cerebro.addsizer(bt.sizers.AllInSizerInt, percents=100)

results = cerebro.run()

# 获取并打印分析结果
for name in data_files.keys():
    sharpe_ratio = results[0].analyzers.getbyname(f'sharpe_{name}').get_analysis()
    drawdown = results[0].analyzers.getbyname(f'drawdown_{name}').get_analysis()
    returns = results[0].analyzers.getbyname(f'returns_{name}').get_analysis()

    print(f'{name} Sharpe Ratio: {round(sharpe_ratio["sharperatio"], 2)}')
    print(f'{name} Drawdown: {round(drawdown["max"]["drawdown"], 2)}%')
    print(f'{name} Total Return: {round(returns["rtot"], 2)}')
    print(f'{name} Annual Return: {round(returns["rnorm100"], 2)}')
    
cerebro.plot(style='candlestick') #用蜡烛图进行绘图