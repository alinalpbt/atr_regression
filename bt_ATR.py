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

    '''next()为每bar调用一次的主逻辑'''
    def next(self):
        if self.order:  
            return     # 检查是否有订单进行中，如果有，就跳过后续逻辑，避免重复下单
        
        current_position = self.broker.getposition(data=self.data).size #获取当前的持仓大小
        target_position = self.get_target_position() #确定目标持仓大小
        
        if target_position != current_position: 
            self.order = self.order_target_size(target=target_position) # 用 order_target_size 方法调整持仓至目标大小
    
    '''计算目标持仓'''
    def get_target_position(self):
        upper_band = self.ema[0] + self.params.atr_multiplier * self.atr[0] #计算上轨 ema200+20ATR
        lower_band = self.ema[0] - self.params.atr_multiplier * self.atr[0] #计算下轨 ema200-20ATR
        size = self.broker.get_cash() / self.data.close[0]  # 理想的全仓大小
        adjusted_size = size  # 初始化 adjusted_size 为全仓大小
        
        if self.data.close[0] == self.ema[0]: #如果收盘价=ema200
            return size  #则全仓
        elif self.data.close[0] <= upper_band and self.data.close[0] > self.ema[0]: #如果收盘价在上轨和ema200之间
            adjusted_size = size * (1 - (self.data.close[0] - self.ema[0]) / (upper_band - self.ema[0]) * 0.5) #修改持仓
            return adjusted_size #返回修改后的目标持仓
        elif self.data.close[0] >= lower_band and self.data.close[0] < self.ema[0]: #如果收盘价在下轨和ema200之间
            adjusted_size = size * (1 + (self.ema[0] - self.data.close[0]) / (self.ema[0] - lower_band) * 1.0) #修改持仓
            return adjusted_size #返回修改后的目标持仓
        return 0

    '''订单状态更新'''
    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]: #如果订单完成、被取消或由于资金不足而被拒绝
            self.order = None  # 重置订单，以便发起新的交易


'''运行回测'''
# 加载QQQ数据
data_qqq = bt.feeds.GenericCSVData(
    dataname='C:/github/atr_regression/results/processed_BATS_QQQ.csv', 
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=5, #volume数据在第f列
    dtformat='%Y-%m-%d %H:%M:%S%z'
)

# 加载SPY数据
data_spy = bt.feeds.GenericCSVData(
    dataname='C:/github/atr_regression/results/processed_BATS_SPY.csv',
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=5,
    dtformat='%Y-%m-%d %H:%M:%S%z'
)

# 加载000300数据
data_000300 = bt.feeds.GenericCSVData(
    dataname='C:/github/atr_regression/results/processed_SSE_DLY_000300.csv',
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=8,
    dtformat='%Y-%m-%d %H:%M:%S%z'
)

cerebro = bt.Cerebro() #初始化 Cerebro
cerebro.adddata(data_qqq)
cerebro.adddata(data_spy)
cerebro.adddata(data_000300) #将前面加载的市场数据添加到Cerebro引擎
cerebro.addstrategy(ATR_Regression_Strategy) #向Cerebro引擎添加策略

cerebro.broker.setcash(10000) # 设置初始资金
cerebro.addsizer(bt.sizers.AllInSizerInt, percents=100)  # 使用全部可用资金进行交易

# 添加资金曲线、最大回撤和年化数据分析器
cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='time_return')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0, timeframe=bt.TimeFrame.Days)

results = cerebro.run()

# 获取分析结果
time_return = results[0].analyzers.time_return.get_analysis()
drawdown = results[0].analyzers.drawdown.get_analysis()
sharpe = results[0].analyzers.sharpe.get_analysis()

# 输出分析结果
print('Time Return:', time_return)
print('Drawdown:', drawdown)
print('Sharpe Ratio:', sharpe)

cerebro.plot(style='candlestick') #用蜡烛图进行绘图