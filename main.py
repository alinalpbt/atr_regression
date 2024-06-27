# main.py

import backtrader as bt
import pandas as pd
from strategy import ATR_Regression_Strategy
import config

def run_backtest():
    cerebro = bt.Cerebro()

    for name, file in config.data_files.items():
        data = bt.feeds.GenericCSVData(
            dataname=f'C:/github/atr_regression/results/{file}',
            datetime=0, open=1, high=2, low=3, close=4, volume=5,
            dtformat='%Y-%m-%d %H:%M:%S%z'
        )
        data._name = name
        cerebro.adddata(data)
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name=f'sharpe_{name}')
        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name=f'returns_{name}')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name=f'drawdown_{name}')

    cerebro.addstrategy(ATR_Regression_Strategy)
    cerebro.broker.setcash(config.initial_cash)
    cerebro.addsizer(bt.sizers.AllInSizerInt, percents=100)

    print("Running backtest...")
    results = cerebro.run()
    print("Backtest completed.")

    for i, result in enumerate(results):
        print(f'--- Strategy {i+1} ---')
        for name in config.data_files.keys():
            sharpe_ratio = result.analyzers.getbyname(f'sharpe_{name}').get_analysis()
            drawdown = result.analyzers.getbyname(f'drawdown_{name}').get_analysis()
            returns = result.analyzers.getbyname(f'returns_{name}').get_analysis()

            print(f'{name} Analysis Results: {list(returns.keys())}')  # 打印所有返回的键值对的键

            sharpe_ratio_value = round(sharpe_ratio["sharperatio"], 2) if "sharperatio" in sharpe_ratio else None
            drawdown_value = round(drawdown["max"]["drawdown"], 2) if "max" in drawdown and "drawdown" in drawdown["max"] else None
            total_return = round(returns.get("rtot", 0), 2) if "rtot" in returns else None
            annual_return = round(returns.get("rnorm100", 0), 2) if "rnorm100" in returns else None

            print(f'{name} Sharpe Ratio: {sharpe_ratio_value}')
            print(f'{name} Drawdown: {drawdown_value}%')
            print(f'{name} Total Return: {total_return}')
            print(f'{name} Annual Return: {annual_return}')

    cerebro.plot(style='candlestick')
    print("Plotting completed.")

if __name__ == '__main__':
    run_backtest()
