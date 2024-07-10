import backtrader as bt
import config
from strategy import VADStrategy
from strategy import BuyAndHoldStrategy
# from strategy import ATR_Regression_Strategy
from texttable import Texttable 
from my_data import MyCSVData
import pandas as pd
from LTanalyzer import LongTermTradeAnalyzer, CalculateTotalReturn, CalculateAnnualReturn
from LTanalyzer import CalculateMaxDrawdown,CalculateSharpeRatio
import os
import matplotlib.pyplot as plt

'''
运行回测
'''
# plt.switch_backend('agg')

# 确保结果目录存在
output_dir = 'data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def add_data_and_run_strategy(strategy_class, data_file, name, strategy_name):
    cerebro = bt.Cerebro()
    data = MyCSVData( 
        dataname=data_file,
        dtformat='%Y/%m/%d %H:%M',
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        fromdate=pd.to_datetime(config.backtest_params['start_date']),
        todate=pd.to_datetime(config.backtest_params['end_date'])
    )
    
    # 添加数据、策略
    cerebro.adddata(data, name=name)
    cerebro.addstrategy(strategy_class)

    # 添加资金、佣金、滑点
    cerebro.broker.setcash(config.broker_params['initial_cash'])
    cerebro.broker.setcommission(config.broker_params['commission_rate'])
    cerebro.broker.set_slippage_perc(config.broker_params['slippage'])
    
    # 添加分析器
    cerebro.addanalyzer(LongTermTradeAnalyzer, _name='longterm_trades')
    cerebro.addanalyzer(CalculateTotalReturn, _name='total_return')
    cerebro.addanalyzer(CalculateAnnualReturn, _name='annual_return')
    cerebro.addanalyzer(CalculateMaxDrawdown, _name='max_drawdown')
    cerebro.addanalyzer(CalculateSharpeRatio, _name='sharpe_ratio')
    
    # 运行回测
    results = cerebro.run()

    # 获取回测时间
    start_date = pd.to_datetime(config.backtest_params['start_date']).strftime('%Y-%m-%d')
    end_date = pd.to_datetime(config.backtest_params['end_date']).strftime('%Y-%m-%d')

    # # 绘图
    # fig = cerebro.plot(style='candlestick', volume=False)[0][0]
    # fig.savefig(f'{output_dir}/{name}_{strategy_name}_plot.png') 
    # plt.close(fig)

    return results, start_date, end_date

def log_trades(trades, file_name, strategy_name):
    file_path = os.path.join(output_dir, file_name)

    try:
        with open(file_path, 'w') as f:
            if strategy_name == 'VADStrategy':
                f.write("Date,IsBuy,Price,Size,Value,PnL,x,ema200,atr,y,TargetPosition,CurrentPosition,Closed\n")
            else:
                f.write("Date,IsBuy,Price,Size,Value,PnL,Closed\n")
            
            for trade in trades['trades']:
                if strategy_name == 'VADStrategy':
                    log_str = f'{trade["date"]},{trade["isbuy"]},{trade["price"]},{trade["size"]},{trade["value"]},{trade["pnl"]},{trade.get("x", "")},{trade.get("ema200", "")},{trade.get("atr", "")},{trade.get("y", "")},{trade.get("target_position", "")},{trade.get("current_position", "")},{trade["closed"]}\n'
                else:
                    log_str = f'{trade["date"]},{trade["isbuy"]},{trade["price"]},{trade["size"]},{trade["value"]},{trade["pnl"]},{trade["closed"]}\n'
                f.write(log_str)
        print(f"每笔交易数据成功写入 {file_path}")
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")


def run_backtest():
    for name, data_file in config.data_files:
        print(f"\n{name} 分析结果:")

        # 运行策略
        buy_and_hold_results, start_date, end_date = add_data_and_run_strategy(BuyAndHoldStrategy, data_file, name, 'BuyAndHoldStrategy')
        buy_and_hold_strat = buy_and_hold_results[0]
        VADStrategy_results, start_date, end_date = add_data_and_run_strategy(VADStrategy, data_file, name, 'VADStrategy')
        VADStrategy_strat = VADStrategy_results[0]
        # atr_regression_results, _, _ = add_data_and_run_strategy(ATR_Regression_Strategy, data_file, name)
        # atr_regression_strat = atr_regression_results[0]

        # 获取 BuyAndHoldStrategy 的分析结果
        buy_and_hold_trades = buy_and_hold_strat.analyzers.longterm_trades.get_analysis()
        buy_and_hold_total_return = buy_and_hold_strat.analyzers.total_return.get_analysis()['total_return']
        buy_and_hold_annual_return = buy_and_hold_strat.analyzers.annual_return.get_analysis()['annual_return']
        buy_and_hold_drawdown = buy_and_hold_strat.analyzers.max_drawdown.get_analysis()['max_drawdown']
        buy_and_hold_sharpe = buy_and_hold_strat.analyzers.sharpe_ratio.get_analysis()['sharpe_ratio']
        buy_and_hold_start_value = buy_and_hold_strat.analyzers.total_return.start_value
        buy_and_hold_end_value = buy_and_hold_strat.analyzers.total_return.end_value

        # 获取 VADStrategy 的分析结果
        VAD_trades = VADStrategy_strat.analyzers.longterm_trades.get_analysis()
        VAD_total_return = VADStrategy_strat.analyzers.total_return.get_analysis()['total_return'] 
        VAD_annual_return = VADStrategy_strat.analyzers.annual_return.get_analysis()['annual_return'] 
        VAD_drawdown = VADStrategy_strat.analyzers.max_drawdown.get_analysis()['max_drawdown']
        VAD_sharpe = VADStrategy_strat.analyzers.sharpe_ratio.get_analysis()['sharpe_ratio']
        VAD_start_value = VADStrategy_strat.analyzers.total_return.start_value
        VAD_end_value = VADStrategy_strat.analyzers.total_return.end_value

        # 获取atr_regression的分析结果
        # atr_regression_trades = atr_regression_strat.analyzers.longterm_trades.get_analysis()
        # atr_total_return = atr_regression_strat.analyzers.total_return.get_analysis()['total_return'] 
        # atr_annual_return = atr_regression_strat.analyzers.annual_return.get_analysis()['annual_return'] 
        # atr_regression_drawdown = atr_regression_strat.analyzers.max_drawdown.get_analysis()['max_drawdown']
        # atr_regression_sharpe = atr_regression_strat.analyzers.sharpe_ratio.get_analysis()['sharpe_ratio']
        # atr_start_value = atr_regression_strat.analyzers.total_return.start_value
        # atr_end_value = atr_regression_strat.analyzers.total_return.end_value

        # 计算超额收益
        excess_total_returns = VAD_total_return - buy_and_hold_total_return
        excess_annual_returns = VAD_annual_return - buy_and_hold_annual_return

        # 打印
        print(f"回测时间：从 {start_date} 到 {end_date}")
        print(f'BuyAndHold 初始本金为 {buy_and_hold_start_value:.2f}')
        print(f'BuyAndHold 最终本金为 {buy_and_hold_end_value:.2f}')
        print(f'VADStrategy 初始本金为 {VAD_start_value:.2f}')
        print(f'VADStrategy 最终本金为 {VAD_end_value:.2f}')

        table = Texttable()
        table.add_rows([
            ["分析项目", "VADStrategy", "BuyAndHold", "超额收益"],
            ["总收益率", f"{VAD_total_return * 100:.2f}%" if VAD_total_return is not None else "N/A",
                            f"{buy_and_hold_total_return * 100:.2f}%" if buy_and_hold_total_return is not None else "N/A",
                            f"{excess_total_returns * 100:.2f}%" if excess_total_returns is not None else "N/A"],
            ["年化收益率", f"{VAD_annual_return * 100:.2f}%" if VAD_annual_return is not None else "N/A",
                            f"{buy_and_hold_annual_return * 100:.2f}%" if buy_and_hold_annual_return is not None else "N/A", 
                            f"{excess_annual_returns * 100:.2f}%" if excess_annual_returns is not None else "N/A"],
            ["最大回撤", f"{VAD_drawdown * 100:.2f}%" if VAD_drawdown is not None else "N/A",
                         f"{buy_and_hold_drawdown * 100:.2f}%" if buy_and_hold_drawdown is not None else "N/A", 
                         " "],
            ["夏普比率", f"{VAD_sharpe:.2f}" if VAD_sharpe is not None else "N/A",
                         f"{buy_and_hold_sharpe:.2f}" if buy_and_hold_sharpe is not None else "N/A", 
                         " "],
            ["总交易笔数", VADStrategy_strat.buy_count + VADStrategy_strat.sell_count,
                          buy_and_hold_strat.buy_count + buy_and_hold_strat.sell_count,
                          " "]
        ])

        print(table.draw())
        log_trades(buy_and_hold_trades, f'{name}_buy_and_hold_trades.csv', 'BuyAndHoldStrategy')
        log_trades(VAD_trades, f'{name}_VAD_trades.csv', 'VADStrategy')

if __name__ == '__main__':
    run_backtest()