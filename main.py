import backtrader as bt
import config
from strategy import ATR_Regression_Strategy

def run_backtest():
    for name, data_file in config.data_files: 
        cerebro = bt.Cerebro()

        data = bt.feeds.GenericCSVData( 
            dataname=data_file,
            dtformat='%Y-%m-%d %H:%M:%S%z',
            datetime=0,
            open=1,
            high=2,
            low=3,
            close=4,
            volume=5
        )
        data._name = name
        cerebro.adddata(data, name=name)

        cerebro.addstrategy(ATR_Regression_Strategy)
        cerebro.broker.setcash(config.initial_cash)
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

        results = cerebro.run()
        strat = results[0]

        # 获取并打印每个数据源的总收益、年化收益、回撤、夏普比率
        print(f"\n{name} 分析结果:")
        returns = strat.analyzers.returns.get_analysis()
        sharpe = strat.analyzers.sharpe.get_analysis()
        drawdown = strat.analyzers.drawdown.get_analysis()

        # 打印总收益、年化收益、回撤、夏普比率
        if 'rtot' in returns:
            print(f"总收益率: {returns['rtot'] * 100:.2f}%")
        if 'rnorm100' in returns:
            print(f"年化收益率: {returns['rnorm100']:.2f}%")
        if 'max' in drawdown:
            print(f"最大回撤: {drawdown['max']['drawdown']:.2f}%")
        if 'sharperatio' in sharpe:
            print(f"夏普比率: {sharpe['sharperatio']:.2f}")

if __name__ == '__main__':
    run_backtest()